import BaseComponent from "../../base.component";

export default class CreateNew extends BaseComponent {
  // Locators
  programmeTitle = 'h6[data-cy="program-title"]';
  // Texts
  textProgrammeTitle = "Programme";
  // Elements
  getProgrammeTitle = () => cy.get(this.programmeTitle);
  checkElementsOnPage() {
    this.getProgrammeTitle().contains(this.textProgrammeTitle);
  }
}
