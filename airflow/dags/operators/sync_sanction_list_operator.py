from .base import DjangoOperator


class SyncSanctionListOperator(DjangoOperator):
    def try_execute(self, context):
        from hct_mis_api.apps.sanction_list.tasks.load_xml import LoadSanctionListXMLTask

        task = LoadSanctionListXMLTask()
        task.execute()
