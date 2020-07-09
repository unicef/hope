from .base import DjangoOperator


class SyncSanctionListOperator(DjangoOperator):
    def execute(self, context):
        from sanction_list.tasks.load_xml import LoadSanctionListXMLTask

        task = LoadSanctionListXMLTask()
        task.execute()
