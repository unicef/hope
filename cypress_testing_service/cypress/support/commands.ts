Cypress.Commands.add('parseXlsx', (inputFile) => {
  return cy.task('parseXlsx', { filePath: inputFile });
});
