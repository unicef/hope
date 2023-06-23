import BaseComponent from "../../base.component";

export default class Grievance extends BaseComponent {
  // Locators
  titlePage = 'h5[data-cy="page-header-title"]';
  searchFilter = 'div[data-cy="filters-search"]';
  ticketIdFilter = 'div[data-mui-test="SelectDisplay"]';
  creationDateFromFilter = 'div[data-cy="filters-creation-date-from"]';
  creationDateToFilter = 'div[data-cy="filters-creation-date-to"]';
  fspFilter = 'div[data-cy="filters-fsp"]';
  categoryFilter = 'div[data-cy="filters-category"]';
  assigneeFilter = 'div[data-cy="filters-assignee"]';
  adminLevelFilter = 'div[data-cy="filters-admin-level"]';
  registrationDataImportFilter =
    'div[data-cy="filters-registration-data-import"]';
  preferredLanguageFilter = 'div[data-cy="filters-preferred-language"]';
  priorityFilter = 'div[data-cy="filters-priority';
  urgencyFilter = 'div[data-cy="filters-urgency';
  activeTicketsFilter = 'div[data-cy="filters-active-tickets';
  buttonApply = 'button[data-cy="button-filters-apply"]';
  buttonClear = 'button[data-cy="button-filters-clear"]';
  buttonNewTicket = 'a[data-cy="button-new-ticket"]';

  tabTitle = 'h6[data-cy="table-title"]';
  tabStatus = 'th[data-cy="status"]';
  // Texts
  // Elements
}
