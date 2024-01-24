from page_object.base_components import BaseComponents


class CommunicationPage(BaseComponents):

    # Locators
    titlePage = 'h5[data-cy="page-header-title"]'
    rows = 'tr[role="checkbox"]'
    buttonApply = 'button[data-cy="button-filters-apply"]'
    buttonClear = 'button[data-cy="button-filters-clear"]'
