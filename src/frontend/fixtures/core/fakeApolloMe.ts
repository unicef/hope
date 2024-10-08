import { MeDocument } from '../../src/__generated__/graphql';

export const fakeApolloMe = [
  {
    request: {
      query: MeDocument,
      variables: {},
    },
    result: {
      data: {
        me: {
          id: 'VXNlck5vZGU6YjYzMWUyY2ItMDg1Yi00ODI0LTk3MmYtMDZmMDIxNjgzYzNj',
          username: 'macsk@tix.com',
          email: 'macsk@tix.com',
          firstName: 'Mac',
          lastName: 'Szew',
          businessAreas: {
            edges: [
              {
                node: {
                  id:
                    'VXNlckJ1c2luZXNzQXJlYU5vZGU6YmZlOWNhZDItZWFlNi00NzZiLTk4NGUtMjFlOTNlY2MyNzNm',
                  name: 'Afghanistan',
                  slug: 'afghanistan',
                  permissions: [
                    'GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR',
                    'PAYMENT_VERIFICATION_CREATE',
                    'GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER',
                    'PROGRAMME_VIEW_LIST_AND_DETAILS',
                    'GRIEVANCES_UPDATE_AS_OWNER',
                    'GRIEVANCES_SET_ON_HOLD_AS_CREATOR',
                    'GRIEVANCES_ADD_NOTE_AS_CREATOR',
                    'PROGRAMME_REMOVE',
                    'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR',
                    'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE',
                    'RDI_RERUN_DEDUPE',
                    'PAYMENT_VERIFICATION_EXPORT',
                    'GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR',
                    'DASHBOARD_EXPORT',
                    'RDI_IMPORT_DATA',
                    'TARGETING_REMOVE',
                    'PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS',
                    'PAYMENT_VERIFICATION_UPDATE',
                    'GRIEVANCES_SEND_FOR_APPROVAL_AS_CREATOR',
                    'GRIEVANCES_SEND_BACK_AS_CREATOR',
                    'GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER',
                    'GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR',
                    'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER',
                    'GRIEVANCES_VIEW_HOUSEHOLD_DETAILS',
                    'GRIEVANCES_APPROVE_FLAG_AND_DEDUPE',
                    'TARGETING_LOCK',
                    'POPULATION_VIEW_HOUSEHOLDS_LIST',
                    'GRIEVANCES_ADD_NOTE',
                    'PAYMENT_VERIFICATION_VIEW_LIST',
                    'GRIEVANCE_ASSIGN',
                    'TARGETING_SEND',
                    'GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR',
                    'TARGETING_VIEW_DETAILS',
                    'PAYMENT_VERIFICATION_FINISH',
                    'GRIEVANCES_UPDATE_AS_CREATOR',
                    'GRIEVANCES_ADD_NOTE_AS_OWNER',
                    'PROGRAMME_UPDATE',
                    'GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE',
                    'PAYMENT_VERIFICATION_ACTIVATE',
                    'RDI_VIEW_DETAILS',
                    'GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER',
                    'GRIEVANCES_VIEW_LIST_SENSITIVE',
                    'GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER',
                    'GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK',
                    'GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR',
                    'PAYMENT_VERIFICATION_VIEW_DETAILS',
                    'DASHBOARD_VIEW_COUNTRY',
                    'TARGETING_DUPLICATE',
                    'GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER',
                    'USER_MANAGEMENT_VIEW_LIST',
                    'TARGETING_VIEW_LIST',
                    'RDI_REFUSE_IMPORT',
                    'GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER',
                    'GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR',
                    'REPORTING_EXPORT',
                    'GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR',
                    'GRIEVANCES_SET_IN_PROGRESS_AS_OWNER',
                    'TARGETING_UNLOCK',
                    'GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR',
                    'GRIEVANCES_SEND_FOR_APPROVAL',
                    'PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS',
                    'GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE',
                    'PROGRAMME_CREATE',
                    'ALL_VIEW_PII_DATA_ON_LISTS',
                    'ACTIVITY_LOG_DOWNLOAD',
                    'RDI_VIEW_LIST',
                    'GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER',
                    'GRIEVANCES_CLOSE_TICKET_FEEDBACK',
                    'GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER',
                    'GRIEVANCES_SEND_FOR_APPROVAL_AS_OWNER',
                    'RDI_MERGE_IMPORT',
                    'PROGRAMME_FINISH',
                    'GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER',
                    'GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR',
                    'GRIEVANCES_SET_ON_HOLD_AS_OWNER',
                    'GRIEVANCES_CREATE',
                    'GRIEVANCES_VIEW_DETAILS_SENSITIVE',
                    'POPULATION_VIEW_HOUSEHOLDS_DETAILS',
                    'GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR',
                    'GRIEVANCES_SEND_BACK',
                    'PAYMENT_VERIFICATION_VERIFY',
                    'POPULATION_VIEW_INDIVIDUALS_LIST',
                    'ACTIVITY_LOG_VIEW',
                    'GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR',
                    'PAYMENT_VERIFICATION_IMPORT',
                    'PROGRAMME_ACTIVATE',
                    'TARGETING_CREATE',
                    'GRIEVANCES_SET_IN_PROGRESS',
                    'GRIEVANCES_VIEW_INDIVIDUALS_DETAILS',
                    'GRIEVANCES_APPROVE_DATA_CHANGE',
                    'GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER',
                    'GRIEVANCES_SEND_BACK_AS_OWNER',
                    'PAYMENT_VERIFICATION_DISCARD',
                    'POPULATION_VIEW_INDIVIDUALS_DETAILS',
                    'GRIEVANCES_UPDATE',
                    'GRIEVANCES_SET_ON_HOLD',
                    'TARGETING_UPDATE',
                  ],
                  __typename: 'UserBusinessAreaNode',
                },
                __typename: 'UserBusinessAreaNodeEdge',
              },
              {
                node: {
                  id:
                    'VXNlckJ1c2luZXNzQXJlYU5vZGU6NTdiMWUyOWItNGQ4MS00MjA2LWE1YjMtNzJlMWJkZGM2Mzc3',
                  name: 'Global',
                  slug: 'global',
                  permissions: [
                    'GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR',
                    'PAYMENT_VERIFICATION_CREATE',
                    'GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER',
                    'PROGRAMME_VIEW_LIST_AND_DETAILS',
                    'GRIEVANCES_UPDATE_AS_OWNER',
                    'GRIEVANCES_SET_ON_HOLD_AS_CREATOR',
                    'GRIEVANCES_ADD_NOTE_AS_CREATOR',
                    'PROGRAMME_REMOVE',
                    'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR',
                    'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE',
                    'RDI_RERUN_DEDUPE',
                    'PAYMENT_VERIFICATION_EXPORT',
                    'GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR',
                    'DASHBOARD_EXPORT',
                    'RDI_IMPORT_DATA',
                    'TARGETING_REMOVE',
                    'PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS',
                    'PAYMENT_VERIFICATION_UPDATE',
                    'GRIEVANCES_SEND_FOR_APPROVAL_AS_CREATOR',
                    'GRIEVANCES_SEND_BACK_AS_CREATOR',
                    'GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER',
                    'GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR',
                    'GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER',
                    'GRIEVANCES_VIEW_HOUSEHOLD_DETAILS',
                    'GRIEVANCES_APPROVE_FLAG_AND_DEDUPE',
                    'TARGETING_LOCK',
                    'POPULATION_VIEW_HOUSEHOLDS_LIST',
                    'GRIEVANCES_ADD_NOTE',
                    'PAYMENT_VERIFICATION_VIEW_LIST',
                    'GRIEVANCE_ASSIGN',
                    'TARGETING_SEND',
                    'GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR',
                    'TARGETING_VIEW_DETAILS',
                    'PAYMENT_VERIFICATION_FINISH',
                    'GRIEVANCES_UPDATE_AS_CREATOR',
                    'GRIEVANCES_ADD_NOTE_AS_OWNER',
                    'PROGRAMME_UPDATE',
                    'GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE',
                    'PAYMENT_VERIFICATION_ACTIVATE',
                    'RDI_VIEW_DETAILS',
                    'GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER',
                    'GRIEVANCES_VIEW_LIST_SENSITIVE',
                    'GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER',
                    'GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK',
                    'GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR',
                    'PAYMENT_VERIFICATION_VIEW_DETAILS',
                    'DASHBOARD_VIEW_COUNTRY',
                    'TARGETING_DUPLICATE',
                    'GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER',
                    'USER_MANAGEMENT_VIEW_LIST',
                    'TARGETING_VIEW_LIST',
                    'RDI_REFUSE_IMPORT',
                    'GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER',
                    'GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR',
                    'REPORTING_EXPORT',
                    'GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR',
                    'GRIEVANCES_SET_IN_PROGRESS_AS_OWNER',
                    'TARGETING_UNLOCK',
                    'GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR',
                    'GRIEVANCES_SEND_FOR_APPROVAL',
                    'PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS',
                    'GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE',
                    'PROGRAMME_CREATE',
                    'ALL_VIEW_PII_DATA_ON_LISTS',
                    'ACTIVITY_LOG_DOWNLOAD',
                    'RDI_VIEW_LIST',
                    'GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER',
                    'GRIEVANCES_CLOSE_TICKET_FEEDBACK',
                    'GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER',
                    'GRIEVANCES_SEND_FOR_APPROVAL_AS_OWNER',
                    'RDI_MERGE_IMPORT',
                    'PROGRAMME_FINISH',
                    'GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER',
                    'GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR',
                    'GRIEVANCES_SET_ON_HOLD_AS_OWNER',
                    'GRIEVANCES_CREATE',
                    'GRIEVANCES_VIEW_DETAILS_SENSITIVE',
                    'POPULATION_VIEW_HOUSEHOLDS_DETAILS',
                    'GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR',
                    'GRIEVANCES_SEND_BACK',
                    'PAYMENT_VERIFICATION_VERIFY',
                    'POPULATION_VIEW_INDIVIDUALS_LIST',
                    'ACTIVITY_LOG_VIEW',
                    'GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR',
                    'PAYMENT_VERIFICATION_IMPORT',
                    'PROGRAMME_ACTIVATE',
                    'TARGETING_CREATE',
                    'GRIEVANCES_SET_IN_PROGRESS',
                    'GRIEVANCES_VIEW_INDIVIDUALS_DETAILS',
                    'GRIEVANCES_APPROVE_DATA_CHANGE',
                    'GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER',
                    'GRIEVANCES_SEND_BACK_AS_OWNER',
                    'PAYMENT_VERIFICATION_DISCARD',
                    'POPULATION_VIEW_INDIVIDUALS_DETAILS',
                    'GRIEVANCES_UPDATE',
                    'GRIEVANCES_SET_ON_HOLD',
                    'TARGETING_UPDATE',
                  ],
                  __typename: 'UserBusinessAreaNode',
                },
                __typename: 'UserBusinessAreaNodeEdge',
              },
            ],
            __typename: 'UserBusinessAreaNodeConnection',
          },
          __typename: 'UserNode',
        },
      },
    },
  },
];
