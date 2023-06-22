import BaseComponent from "../../base.component";

export default class CreateNew extends BaseComponent {
  // Locators
  targetingCriteriaTitle = 'h6[data-cy="title-targeting-criteria"]';
  // Texts
  textTargetingCriteriaTitle = "Targeting Criteria";
  // Elements
  getProgrammeTitle = () => cy.get(this.targetingCriteriaTitle);
  checkElementsOnPage() {
    this.getProgrammeTitle().contains(this.textTargetingCriteriaTitle);
  }
}
