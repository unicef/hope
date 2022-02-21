import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import wait from 'waait';
import { render } from '../../testUtils/testUtils';
import { AllProgramsDocument } from '../../__generated__/graphql';
import { ExampleComponent } from './ExampleComponent';

const mocks = [
  {
    request: {
      query: AllProgramsDocument,
      variables: { businessArea: 'afghanistan' },
    },
    result: {
      data: {
        allPrograms: {
          pageInfo: {
            hasNextPage: true,
            hasPreviousPage: false,
            endCursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            __typename: 'PageInfo',
          },
          totalCount: 9,
          edgeCount: 5,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UHJvZ3JhbU5vZGU6ZDM4YWI4MTQtOTQyNy00ZmJkLTg4ODctOGUyYzlkMzcxYjg2',
                name: 'Notice hair fall college enough perhaps.',
                startDate: '2020-01-20',
                endDate: '2020-08-19',
                status: 'ACTIVE',
                caId: '123-21-PRG-00001',
                description:
                  'Purpose she occur lose new wish day per little because east like bill.',
                budget: '691946197.49',
                frequencyOfPayments: 'ONE_OFF',
                populationGoal: 507376,
                sector: 'EDUCATION',
                totalNumberOfHouseholds: 12,
                individualDataNeeded: true,
                __typename: 'ProgramNode',
              },
              __typename: 'ProgramNodeEdge',
            },
          ],
          __typename: 'ProgramNodeConnection',
        },
      },
    },
  },
];

describe('components/ExampleComponent', () => {
  it('should render', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={mocks}>
        <ExampleComponent />
      </MockedProvider>,
    );
    await wait(0); // wait for response

    expect(container).toMatchSnapshot();
  });
});
