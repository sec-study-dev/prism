# -*- coding: utf-8 -*-
"""PRISM agent prompts as importable modules."""

from . import stage1_1a_doc_proposer as p_1a
from . import stage1_1b_mpg_proposer as p_1b
from . import stage1_1c_merger as p_1c
from . import stage1_1d_critic as p_1d
from . import stage1_1e_aggregator as p_1e
from . import stage1_1f_poc_generator as p_1f
from . import stage3_3a_economic_agent as p_3a
from . import stage3_3b_code_audit_agent as p_3b
from . import stage3_3c_crossval_econ_to_audit as p_3c
from . import stage3_3d_crossval_audit_to_econ as p_3d
from . import stage3_3e_synthesizer as p_3e
from . import schemas

PROMPTS = {
    '1a': p_1a.PROMPT,
    '1b': p_1b.PROMPT,
    '1c': p_1c.PROMPT,
    '1d': p_1d.PROMPT,
    '1e': p_1e.PROMPT,
    '1f': p_1f.PROMPT,
    '3a': p_3a.PROMPT,
    '3b': p_3b.PROMPT,
    '3c': p_3c.PROMPT,
    '3d': p_3d.PROMPT,
    '3e': p_3e.PROMPT,
}

RENDERERS = {
    '1a': p_1a.render,
    '1b': p_1b.render,
    '1c': p_1c.render,
    '1d': p_1d.render,
    '1e': p_1e.render,
    '1f': p_1f.render,
    '3a': p_3a.render,
    '3b': p_3b.render,
    '3c': p_3c.render,
    '3d': p_3d.render,
    '3e': p_3e.render,
}
