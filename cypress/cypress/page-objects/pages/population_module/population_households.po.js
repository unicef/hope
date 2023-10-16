import BaseComponent from "../../base.component";

export default class PopulationHouseholds extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';

  // Texts
  textTitle = "Households";

  // Elements
<<<<<<< HEAD
  clickNavHouseholds() {
    this.getMenuButtonProgrammePopulation().click();
    this.getMenuButtonHouseholds().should("be.visible");
    this.getMenuButtonHouseholds().click();
  }
=======
  getTitle = () => cy.get(this.titlePage);
>>>>>>> 1320d7b3c06f4b8cc0506fbb6d09aaac676921bd
}
