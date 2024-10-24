export interface IntrospectionResultData {
  __schema: {
    types: {
      kind: string;
      name: string;
      possibleTypes: {
        name: string;
      }[];
    }[];
  };
}
const result: IntrospectionResultData = {
  __schema: {
    types: [
      {
        kind: 'INTERFACE',
        name: 'Node',
        possibleTypes: [
          {
            name: 'PaymentRecordNode',
          },
          {
            name: 'HouseholdNode',
          },
          {
            name: 'CashPlanNode',
          },
          {
            name: 'ProgramNode',
          },
          {
            name: 'LocationNode',
          },
        ],
      },
    ],
  },
};
export default result;
