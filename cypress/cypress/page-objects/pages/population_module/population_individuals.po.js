import BaseComponent from "../../base.component";

export default class PopulationIndividuals extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';

  // Texts
  textTitle = "Individuals";

  // Elements
<<<<<<< HEAD

  clickNavIndividuals() {
    this.getMenuButtonProgrammePopulation().click();
    this.getMenuButtonIndividuals().should("be.visible");
    this.getMenuButtonIndividuals().click();
  }
=======
  getTitle = () => cy.get(this.titlePage);
>>>>>>> 1320d7b3c06f4b8cc0506fbb6d09aaac676921bd
}
