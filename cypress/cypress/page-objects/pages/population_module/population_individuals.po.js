import BaseComponent from "../../base.component";

export default class PopulationIndividuals extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';

  // Texts
  textTitle = "Individuals";

  // Elements
  getTitle = () => cy.get(this.titlePage);
}
