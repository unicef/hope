import BaseComponent from "../../base.component";

export default class PMDetailsPage extends BaseComponent {
  // Locators
  pageHeaderTitle = 'h5[data-cy="page-header-title"]';
  // Texts
  // Elements
  getTitle = () => cy.get(this.pageHeaderTitle);
}
