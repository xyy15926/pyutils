#!/usr/bin/env python3
#----------------------------------------------------------
#   Name: stats_model.py
#   Author: xyy15926
#   Created at: 2020-09-07 18:56:01
#   Updated at: 2020-09-07 18:56:02
#   Description:
#----------------------------------------------------------
#%%
import logging
import statsmodels.api as sm

#%%
logger = logging.getLogger("xutils.stats_models")

# %%
def fit_lr_stepwise(dt, tgt, p_in=0.05, p_out=0.05):
    """
    Description:
    select features with stepwise LR

    Params:
    dt: features
    tgt: target
    p_in: upper bound of feature' p-value to move in
    p_out: lower bound of feature' p-value to move out

    Return:
    rets: LR fit results
    _selected: selected features
    _aic, _bic: AIC, BIC of model every time features changed
    """
    _selected, _remained = list(), list(dt.columns)
    _remained.remove("const")
    aics, bics = [], []
    while True:
        # reset `_min_pval` here, so that if `_remained` is
        # null, `_min_pval` could terminate while-loop
        _min_pval, _min_feat = 1, None
        last_rets =  None

        # FORWARD
        for _feat in _remained:
            rets = sm.Logit(tgt, dt[_selected + ["const", _feat]]).fit()
            pvals = rets.pvalues
            if pvals[_feat] < _min_pval:
                _min_pval, _min_feat = pvals[_feat], _feat
                # record the model results when a better feature
                # found to avoid fitting model in backward stage
                last_rets = rets
        # move feature with minimum p-value from `_remained`
        # to `_selected`, if its p-value if small enough
        if _min_pval < p_in:
            logger.info("move `%s` with p-value `%f` into `%s`", _min_feat, _min_pval, _selected)
            _selected.append(_min_feat)
            _remained.remove(_min_feat)
            # record aic, bic
            aics.append(last_rets.aic)
            bics.append(last_rets.bic)
        # no significant features remained, break
        else:
            break

        #BACKWARD
        _max_feat = last_rets.pvalues[_selected].idxmax()
        # move feature with maximum p-value from `_selected`
        # to `_remained`, if its p-value is large enough
        if last_rets.pvalues[_max_feat] > p_out:
            logger.info("remove `%s` with p-value `%f` from `%s`", _min_feat, _min_pval, _selected)
            _selected.remove(_max_feat)
            _remained.append(_max_feat)
            # record aic, bic
            aics.append(last_rets.aic)
            bics.append(last_rets.bic)

    # fit model with selected features
    rets = sm.Logit(tgt, dt[_selected + ["const"]]).fit()
    return rets, _selected, aics, bics


# clf = LR(penalty=None, tol=1e-4, C=float("inf"), fit_intercept=True,
#         class_weight="balanced", random_state=RANDOM_SEED,
#         solver="saga", max_iter=100, warm_start=False,
#         n_jobs=1)
# clf.fit(df_woe[["X1"]], Y)
# clf.coef_
# clf.predict(df_woe[["X1"]])

