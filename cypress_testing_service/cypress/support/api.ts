// TODO: remove
// import promisify from 'cypress-promise';

export const apiUrl = '/api/graphql';

const request = (method: string, body: string | object) => {
  return cy.request(method, apiUrl, body);
};

const api = {
  createProgram(programData) {
    return request('POST', {
      operationName: 'CreateProgram',
      query: `
        mutation CreateProgram($programData: CreateProgramInput!) {
          createProgram(programData: $programData) {
            program {
              id
              name
              status
              startDate
              endDate
              programCaId
              budget
              description
              frequencyOfPayments
              sector
              scope
              cashPlus
              populationGoal
            }
          }
        }
      `,
      variables: { programData },
    });
  },

  updateProgram({ status, ...rest }) {
    return request('POST', {
      operationName: 'UpdateProgram',
      query: `
        mutation UpdateProgram($programData: UpdateProgramInput!) {
          updateProgram(programData: $programData) {
            program {
              id
              name
              startDate
              endDate
              status
              programCaId
              description
              budget
              frequencyOfPayments
              cashPlus
              populationGoal
              scope
              sector
              totalNumberOfHouseholds
              administrativeAreasOfImplementation
            }
          }
        }
      `,
      variables: {
        programData: {
          status: status && status.toUpperCase(),
          ...rest,
        },
      },
    });
  },

  getProgram(businessArea: string, programId: string) {
    return request('POST', {
      operationName: 'AllPrograms',
      query: `
      query AllPrograms($businessArea: String, $id: String) {
        allPrograms(businessArea: $businessArea, id: $id) {
          edges {
            node {
              id
              name
            }
          }
        }
      }
    `,
      variables: { businessArea, programId },
    });
  },

  getAllPrograms(businessArea: string) {
    return request('POST', {
      operationName: 'AllPrograms',
      query: `
      query AllPrograms($businessArea: String) {
        allPrograms(businessArea: $businessArea) {
          pageInfo {
            hasNextPage
          }
          edges {
            node {
              id
              name
            }
          }
        }
      }
    `,
      variables: { businessArea },
    });
  },

  deleteProgram(programId: string) {
    return request('POST', {
      operationName: 'DeleteProgram',
      query: `
        mutation DeleteProgram($programId: String!) {
          deleteProgram(programId: $programId) {
            ok
          }
        }
      `,
      variables: { programId },
    });
  },

  createTargetPopulation(input) {
    return request('POST', {
      operationName: 'CreateTP',
      query: `
        mutation CreateTP($input: CreateTargetPopulationInput!) {
          createTargetPopulation(input: $input) {
            targetPopulation {
              id
              status
              candidateListTotalHouseholds
              candidateListTotalIndividuals
              finalListTotalHouseholds
              finalListTotalIndividuals
            }
          }
        }
      `,
      variables: { input },
    });
  },

  getUploadImportDataXlsxFileOperation() {
    return {
      operationName: 'UploadImportDataXlsxFile',
      query: `
        mutation UploadImportDataXlsxFile($file: Upload!) {
          uploadImportDataXlsxFile(file: $file) {
            errors {
              header
              message
              rowNumber
            }
            importData {
              id
              numberOfIndividuals
              numberOfHouseholds
              registrationDataImport {
                id
              }
            }
          }
        }
      `,
      variables: { file: null },
    };
  },

  createRegistrationDataImport(registrationDataImportData) {
    return request('POST', {
      operationName: 'CreateRegistrationDataImport',
      query: `
        mutation CreateRegistrationDataImport(
          $registrationDataImportData: CreateRegistrationDataImportExcelInput!
        ) {
          createRegistrationDataImport(
            registrationDataImportData: $registrationDataImportData
          ) {
            registrationDataImport {
              id
              name
              dataSource
              datahubId
            }
          }
        }
      `,
      variables: { registrationDataImportData },
    });
  },
};

// TODO don't prefer default export!
// eslint-disable-next-line import/prefer-default-export
export { api };
