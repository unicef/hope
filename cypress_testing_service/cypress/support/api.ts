// TODO: remove
// import promisify from 'cypress-promise';

const request = (method: string, body: string | object) => {
  return cy.request(method, 'api/graphql', body);
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
      variables: { programId }
    });
  }
};

// TODO don't prefer default export!
// eslint-disable-next-line import/prefer-default-export
export { api };
