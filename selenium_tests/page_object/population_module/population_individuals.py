from page_object.base_components import BaseComponents


class class PopulationIndividuals extends BaseComponent {
  // Locators
  // Texts
  // Elements

  clickNavIndividuals() {
    this.getMenuButtonProgrammePopulation().click();
    this.getMenuButtonIndividuals().should("be.visible");
    this.getMenuButtonIndividuals().click();
  }
}
