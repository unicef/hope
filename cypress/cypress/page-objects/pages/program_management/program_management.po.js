import BaseComponent from "../../base.component";

export default class ProgramManagement extends BaseComponent {
  // Locators
  tableRow = 'tr[role="checkbox"]';
  // Texts
  // Elements
  getTableRow = () => cy.get(this.tableRow);
}
