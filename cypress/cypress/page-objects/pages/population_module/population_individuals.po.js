import BaseComponent from "../../base.component";

export default class PopulationIndividuals extends BaseComponent {
  // Locators
  // Texts
  // Elements

  clickNavIndividuals() {
    this.getMenuButtonProgrammePopulation().click();
    this.getMenuButtonIndividuals().should("be.visible");
    this.getMenuButtonIndividuals().click();
  }
}
