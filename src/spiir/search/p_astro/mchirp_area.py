import logging
from pathlib import Path
from typing import Optional, Union, Tuple

import numpy as np

# estimate_source_mass
# get_area
# calc_areas
# predict_redshift
# calc_probabilities
# predict_source_p_astro
# plot_mchirp_area_figure
# _draw_mchirp_area_axes

from pycbc.mchirp_area import calc_areas, get_area

def calculate_probabilities():
    pass

def estimate_redshift():
    pass

class ChirpMassAreaModel:
    def __init__(
        self,
        a0: Optional[float] = None,
        b0: Optional[float] = None,
        b1: Optional[float] = None,
        m0: Optional[float] = None,
        mass_bounds: Tuple[float, float] = (1.0, 45.0),
        ns_max: float = 3.0, 
        mass_gap_max: Optional[float] = None,
        separate_mass_gap: bool = False,
        lal_cosmology: bool = True,
    ):
        """Defines class-based Compact Binary Coalescence source classifier based on
        the PyCBC Chirp Mass Area method by Villa-Ortega et. al. (2021).

        Parameters
        ----------
        a0: float | None
            Model parameter used as the coefficient to estimate BAYESTAR distance from
            the minimum effective distance of a given single instrument event trigger.
        b0: float | None
            Model parameter used to estimate distance uncertainty?
        b1: float | None
            Model parameter used to estimate distance uncertainty?
        m0: float | None
            Inherent percentage uncertainty in chirp mass, set to 1% (0.01) by default.
        mass_bounds: tuple[float, float]
            The upper and lower bounds for both component masses (m1 >= m2).
        ns_max: float
            The boundary that separates a classification between BH and NS.
        mass_gap_max: float | None
            If mass_gap_max is set, we assign a Mass Gap (MG) category above ns_max.
        separate_mass_gap: bool
            If True, splits Mass Gap into BH+Gap, Gap+NS, and Gap+Gap.
        lal_cosmology: bool
            If True, it uses the Planck15 cosmology model
            as defined in lalsuite instead of the astropy default.

        Returns
        -------
        dict[str, float]
            A dictionary of probabilities predicted for each CBC source class.
        """

        self.a0 = a0
        self.b0 = b0
        self.b1 = b1

        self.m0 = m0  # inherent relative uncertainty in chirp mass

        # specify component mass value boundaries
        self.mass_bounds = mass_bounds  # component mass bounds for integration
        self.ns_max = ns_max
        self.mass_gap_max = mass_gap_max  # if None, no mass_gap class provided
        assert 0 < ns_max <= (self.mass_gap_max or ns_max)

        self.separate_mass_gap = separate_mass_gap
        self.lal_cosmology = lal_cosmology

    def __repr__(self, precision: int = 4):
        """Overrides string representation of cls when printed."""
        coefficents = ", ".join(
            [
                f"{key}={self.coefficients[key]!r}"
                if self.coefficients[key] is None
                else f"{key}={self.coefficients[key]:.{precision}f}"
                for key in self.coefficients
            ]
        )
        return f"{type(self).__name__}({coefficents})"

    @property
    def coefficients(self):
        return {"a0": self.a0, "b0": self.b0, "b1": self.b1, "m0": self.m0}

    # define distance estimation functions
    def _estimate_lum_dist(
        self,
        eff_distance: Union[float, np.ndarray],
    ) -> Union[float, np.ndarray]:
        """Function to estimate luminosity distance from the minimum effective distance.

        TODO: Add mathematics and explanation to docstring.
        """
        assert self.a0 is not None, f"a0 coefficient is not initialised."
        return eff_distance * self.a0

    def _estimate_lum_dist_std(
        self,
        eff_distance: Union[float, np.ndarray],
        snr: Union[float, np.ndarray],
    ) -> Union[float, np.ndarray]:
        """Function to estimate standard deviation of luminosity distance.

        TODO: Add mathematics and explanation to docstring.
        """
        assert self.a0 is not None, f"a0 coefficient is not initialised."
        assert self.b0 is not None, f"b0 coefficient is not initialised."
        assert self.b1 is not None, f"b1 coefficient is not initialised."

        lum_dist_std = (
            np.power(snr, self.b0)
            + np.exp(self.b1)
            + self._estimate_lum_dist(eff_distance)
        )

        return lum_dist_std

    def fit(
        self,
        bayestar_distances: np.ndarray,
        bayestar_stds: np.ndarray,
        eff_distances: np.ndarray,
        snrs: np.ndarray,
        m0: Optional[float] = None,
    ):
        """Fits a Chirp Mass Area model with equal length arrays for BAYESTAR luminosity
        distances against corresponding SNRs and (minimum) effective distances
        recovered by a gravitational wave search pipeline.

        The fitted coefficients are saved to the model instance's attributes as a0, b0,
        b1, and m0; and they can be accessed conveniently via the self.coefficients
        property. If m0 is provided but self.m0 is already initialised, m0 will be
        overwritten with the new value.

        This function uses numpy's Polynomial function to fit the coefficients for
        the chirp mass area model - specifically for estimating luminosity distance
        uncertainty (standard deviation) as a function of the estimated BAYESTAR
        luminosty distance and the recovered trigger Signal to Noise (SNR) ratios.

        See: https://numpy.org/doc/stable/reference/routines.polynomials.html

        Parameters
        ----------
        bayestar_distances: np.ndarray
            An array of BAYESTAR approximated luminosity distances as returned by the
            ligo.skymap BAYESTAR algorithm.
        bayestar_stds: np.ndarray
            An array of BAYESTAR approximated luminosity distance standard deviations
            as returned by the ligo.skymap BAYESTAR algorithm.
        eff_distances: np.ndarray
            An array of trigger effective distances recovered from a search pipeline.
        snrs: np.ndarray
            An array of trigger SNR values recovered from a search pipeline.
        m0: float | None
            A constant that defines the uncertainty in chirp mass.
        """
        # specify chirp mass uncertainty constant
        self.m0 = m0 or self.m0
        if self.m0 is None and m0 is None:
            raise ValueError(f"m0 coefficent not initialised - provide a value for m0.")

        # a0 taken as mean ratio between lum dist and (minimum) effective distances)
        self.a0 = float(np.mean(bayestar_distances / eff_distances))

        # estimate BAYESTAR luminosity distances
        bayes_dist_std = bayestar_stds / self._estimate_lum_dist(eff_distances)

        # fit luminosity distance uncertainty as a function of SNR
        b = Polynomial.fit(np.log(snrs), np.log(bayes_dist_std), 1)
        self.b1, self.b0 = b.convert().coef
        logger.info(f"Fitted coefficients for {self.__repr__}.")
        return self

    def predict(
        self,
        mchirp: float,
        snr: float,
        eff_dist: float,
        truncate_lower_dist: Optional[float] = 0.0003,
    ) -> Dict[str, float]:
        """
        Computes the different probabilities that a candidate event belongs to each
        CBC source class according to search.classify.mchirp_areas.calc_probabilities.

        Parameters
        ----------
        mchirp: float
            The source frame chirp mass.
        snr: float
            The coincident signal-to-noise ratio (SNR)
        eff_distance: float
            The estimated effective distance to the event,
            usually taken as the minimum across all coincident detectors.
        truncate_lower_dist: float | None
            If provided, takes the ceiling of truncate_lower_dist and the estimated
            lower uncertainty bound for distance to prevent negative or unrealistic
            distance estimates.

        Returns
        -------
        dict[str, float]
            The astrophysical source probabilities for each class.
        """
        assert self.m0 is not None, f"m0 coefficient is not initialised."
        assert self.a0 is not None, f"a0 coefficient is not initialised."
        assert self.b0 is not None, f"b0 coefficient is not initialised."
        assert self.b1 is not None, f"b1 coefficient is not initialised."

        # calc_probabilities does not type check mutable self.config nor coefficients
        # return predict_source_p_astro(
        #     self.a0,
        #     self.b0,
        #     self.b1,
        #     self.m0,
        #     mchirp,
        #     snr,
        #     eff_dist,
        #     self.mass_bounds,  # component mass bounds
        #     self.ns_max,
        #     self.mass_gap_max,
        #     self.separate_mass_gap,
        #     self.lal_cosmology,
        #     truncate_lower_dist,
        # )

        
        z, z_std = predict_redshift(
            self.a0, self.b0, self.b1,
            snr, eff_distance, lal_cosmology, truncate_lower_dist
        )

        return calc_probabilities(
            self.m0, mchirp, z, z_std, mass_bounds, ns_max, mass_gap_max, separate_mass_gap
        )

    def save_pkl(self, path: Union[str, Path]):
        with Path(path).open(mode="wb") as f:
            pickle.dump(self.__dict__, f)

    def load_pkl(self, path: Union[str, Path]):
        with Path(path).open(mode="rb") as f:
            self.__dict__ = pickle.load(f)

        for key in ["a0", "b0", "b1", "m0"]:
            if getattr(self, key, None) is None:
                logger.info(f"{type(self).__name__} coefficient {key} not initialised.")

    def save_json(self, path: Union[str, Path], indent: int = 4):
        with Path(path).open(mode="w") as f:
            json.dump(self.__dict__, f, indent=indent)

    def load_json(self, path: Union[str, Path]):
        with Path(path).open(mode="r") as f:
            state = json.load(f)
        for key in state:
            setattr(self, key, state[key])

        for key in ["a0", "b0", "b1", "m0"]:
            if getattr(self, key, None) is None:
                logger.info(f"{type(self).__name__} coefficient {key} not initialised.")
