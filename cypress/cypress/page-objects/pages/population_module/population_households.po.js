import BaseComponent from "../../base.component";

export default class PopulationHouseholds extends BaseComponent {
  // Locators
  // Texts
  // Elements
  clickNavHouseholds() {
    this.getMenuButtonProgrammePopulation().click();
    this.getMenuButtonHouseholds().should("be.visible");
    this.getMenuButtonHouseholds().click();
  }
}
