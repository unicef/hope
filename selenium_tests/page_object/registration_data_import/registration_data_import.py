from page_object.base_components import BaseComponents


class RegistrationDataImport(BaseComponents):
    # Locators
    buttonImport = 'button[data-cy="button-import"]'

    # Texts

    # Elements

    def getButtonImport(self):
        return self.wait_for(self.buttonImport)
