import BaseComponent from "../../base.component";

export default class PopulationHouseholds extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';

  // Texts
  textTitle = "Households";

  // Elements
  getTitle = () => cy.get(this.titlePage);
}
