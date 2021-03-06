from __future__ import absolute_import
from __future__ import unicode_literals
from corehq.apps.indicators.views import IndicatorAdminCRUDFormView, BulkCopyIndicatorsView


class MVPIndicatorAdminCRUDFormView(IndicatorAdminCRUDFormView):
    base_loc = "mvp.indicator_admin.forms"


class MVPBulkCopyIndicatorsView(BulkCopyIndicatorsView):
    indicator_loc = "mvp.models"
