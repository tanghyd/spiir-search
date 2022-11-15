"""Module containing the computation of p_astro by source category.

Code sourced from https://git.ligo.org/lscsoft/p-astro/-/tree/master/ligo.
"""

import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from ligo.p_astro import SourceType, MarginalizedPosterior
from ligo.p_astro.computation import (
    p_astro_update, evaluate_p_astro_from_bayesfac, choose_snr, get_f_over_b
)

logger = logging.getLogger(__name__)

class CompositeModel:
    def __init__(
        self,
        fgmc_model: FGMCTwoComponentModel,
        mchirp_area_model: mchirp_area.ChirpMassAreaModel,
    ):
        # to do: intiailise from config file(?)
        self.fgmc_model = fgmc_model
        self.mchirp_area_model = mchirp_area_model

    def predict(    
        self,
        far: float,
        snr: float,
        mchirp: float,
        eff_dist: float,
    ):
        astro_prob = self.fgmc_model.predict(far, snr)
        source_probs = self.mchirp_area_model.predict(mchirp, snr, eff_dist)
        probs = {key: source_probs[key] * astro_prob for key in source_probs}
        probs.update({"Terrestrial": 1 - astro_prob})
        return probs

class FGMCTwoComponentModel:
    def __init__(
        self,
        far_threshold: float = 3e-4,
        snr_threshold: float = 8.5,
        prior_type: str = "Uniform",
    ):
        # set FAR and SNR thresholds to classify as astro source for bayes factor model
        self.far_threshold = far_threshold
        self.snr_threshold = snr_threshold

        # assign prior distribution type to counts
        valid_prior_types = ("Uniform", "Jeffreys")
        if prior_type not in valid_prior_types:
            raise ValueError(f"{prior_type} must be one of {valid_prior_types}.")
        self.prior_type = prior_type

        # mean posterior counts
        self.mean_counts = None

    def __repr__(self, precision: int = 4):
        """Overrides string representation of cls when printed."""
        if self.mean_counts is not None:
            mean_counts = ", ".join(
                [
                    f"{key}={self.mean_counts[key]:.{precision}f}"
                    for key in self.mean_counts
                ]
            )
            return f"{type(self).__name__}({mean_counts})"
        else:
            return f"{type(self).__name__}()"

    def fit(self, far: np.ndarray, snr: np.ndarray):
        # approximate bayes factor
        bayes_factors = get_f_over_b(far, snr, self.far_threshold, self.snr_threshold)
        assert len(bayes_factors.shape) == 1, "bayes_factors should be a 1-dim array."

        astro = SourceType(label="Astro", w_fgmc=np.ones(len(bayes_factors)))
        terr = SourceType(label="Terr", w_fgmc=np.ones(len(bayes_factors)))
        self.marginalized_posterior = MarginalizedPosterior(
            f_divby_b=bayes_factors,
            prior_type=self.prior_type,
            terr_source=terr,
            **{"Astro": astro},
        )

        # idx = bayes_factors >= min(bayes_factors)
        # p_astro_values = marginalized_posterior.pastro(categories=["Astro"], trigger_idx=idx)

        self.mean_counts = {
            key: self.marginalized_posterior.getOneDimMean(category=key)
            for key in ("Astro", "Terr")
        }

        return self

    def predict(
        self, far: Union[float, np.ndarray], snr: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        bayes_factors = get_f_over_b(far, snr, self.far_threshold, snr_threshold)
        return self.marginalized_posterior.pastro_update(
            categories=["Astro"],
            bayesfac_dict={"Astro": bayes_factors},
            mean_values_dict=self.mean_counts,
        )

    def save_pkl(self, path: Union[str, Path]):
        with Path(path).open(mode="wb") as f:
            pickle.dump(self.__dict__, f)

    def load_pkl(self, path: Union[str, Path]):
        with Path(path).open(mode="rb") as f:
            self.__dict__ = pickle.load(f)
