from core.kobo.api import KoboAPI


class RdiKoboImport:

    def __init__(self, uid, business_area):
        self.submissions = KoboAPI(business_area).get_project_submissions(uid)

