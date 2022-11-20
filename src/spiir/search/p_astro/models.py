"""Module containing the computation of p_astro by source category.

Code sourced from https://git.ligo.org/lscsoft/p-astro/-/tree/master/ligo.
"""

import logging
import pickle
from pathlib import Path
from typing import Dict, Optional, Union

import numpy as np
from ligo.p_astro import MarginalizedPosterior, SourceType
from ligo.p_astro.computation import get_f_over_b

from .mchirp_area import ChirpMassAreaModel

logger = logging.getLogger(__name__)


class TwoComponentModel:
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
        self.marginalized_posterior: Optional[MarginalizedPosterior] = None
        self.mean_counts: Optional[Dict[str, float]] = None

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

        # construct two component posterior for signal vs. noise
        astro = SourceType(label="Astro", w_fgmc=np.ones(len(bayes_factors)))
        terr = SourceType(label="Terr", w_fgmc=np.ones(len(bayes_factors)))
        self.marginalized_posterior = MarginalizedPosterior(
            f_divby_b=bayes_factors,
            prior_type=self.prior_type,
            terr_source=terr,
            **{"Astro": astro},
        )

        # update expected mean counts given observed data
        self.mean_counts = {
            key: self.marginalized_posterior.getOneDimMean(category=key)
            for key in ("Astro", "Terr")
        }

        return self

    def predict(self, far: float, snr: float) -> float:
        assert self.marginalized_posterior is not None, "Model not fit - call .fit()."
        bayes_factors = get_f_over_b(far, snr, self.far_threshold, self.snr_threshold)
        return self.marginalized_posterior.pastro_update(
            categories=["Astro"],
            bayesfac_dict={"Astro": bayes_factors},
            mean_values_dict=self.mean_counts,
        )

    def save(self, path: Union[str, Path]):
        file_path = Path(path)
        if file_path.suffix == ".pkl":
            self.save_pkl(file_path)
        elif file_path.suffix == ".json":
            raise NotImplementedError("JSON compatibility not yet implemented.")
        else:
            raise RuntimeError(
                f"Save failed - cannot detect file type: {file_path.suffix}. "
                "Valid file types are '.pkl'."
            )

    def load(self, path: Union[str, Path]):
        file_path = Path(path)
        if file_path.suffix == ".pkl":
            self.load_pkl(file_path)
        elif file_path.suffix == ".json":
            raise NotImplementedError("JSON compatibility not yet implemented.")
        else:
            raise RuntimeError(
                f"Save failed - cannot detect file type: {file_path.suffix}. "
                "Valid file types are '.pkl'."
            )

    def save_pkl(self, path: Union[str, Path]):
        with Path(path).open(mode="wb") as f:
            pickle.dump(self.__dict__, f)

    def load_pkl(self, path: Union[str, Path]):
        with Path(path).open(mode="rb") as f:
            self.__dict__ = pickle.load(f)


class CompositeModel:
    def __init__(
        self,
        signal_model: Optional[TwoComponentModel] = None,
        source_model: Optional[ChirpMassAreaModel] = None,
    ):
        self.signal_model = signal_model or TwoComponentModel()
        self.source_model = source_model or ChirpMassAreaModel()

    def load(
        self,
        signal_config: str,
        source_config: str,
    ):
        self.signal_model.load(signal_config)
        self.source_model.load(source_config)

    def predict(
        self,
        far: float,
        snr: float,
        mchirp: float,
        eff_dist: float,
    ) -> Dict[str, float]:
        astro_prob = self.signal_model.predict(far, snr)
        source_probs = self.source_model.predict(mchirp, snr, eff_dist)
        probs = {key: source_probs[key] * astro_prob for key in source_probs}
        probs.update({"Terrestrial": 1 - astro_prob})
        return probs
