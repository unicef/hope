from page_object.base_components import BaseComponents


class CreateNew extends BaseComponent {
  // Locators
  targetingCriteria = 'h6[data-cy="title-targeting-criteria"]';
  // Texts
  textTargetingCriteria = "Targeting Criteria";
  // Elements
  getTargetingCriteria = () => cy.get(this.targetingCriteria);
  checkElementsOnPage() {
    this.getTargetingCriteria().contains(this.textTargetingCriteria);
  }
}
