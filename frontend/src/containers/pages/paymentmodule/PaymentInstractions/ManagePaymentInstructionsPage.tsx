import { Box } from '@material-ui/core';
import React, { useState } from 'react';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { usePermissions } from '../../../../hooks/usePermissions';
import { ManagePaymentInstructionsHeader } from '../../../../components/paymentmodule/ManagePaymentInstructions/ManagePaymentInstructionsHeader';
import { PaymentInstructionItem } from '../../../../components/paymentmodule/ManagePaymentInstructions/PaymentInstructionItem';

const initialItems = [
  {
    id: 'PI-946/12',
    unicefId: 'PI-946/12',
    status: 'PENDING',
    deliveryMechanism: 'Mobile Money',
    fsp: 'CityGroup',
    criteria: [
      {
        filters: [
          {
            comparisonMethod: 'EQUALS',
            arguments: ['AF0904'],
            fieldName: 'admin2',
            isFlexField: false,
            fieldAttribute: {
              labelEn: `Household resides in which \${admin2_h_c}?`,
              type: 'SELECT_ONE',
              choices: [
                {
                  labels: [
                    {
                      label: 'Doshi-AF0904',
                      language: 'English(EN)',
                      __typename: 'LabelNode',
                    },
                  ],
                  labelEn: 'Doshi-AF0904',
                  value: 'AF0904',
                  admin: null,
                  listName: null,
                  __typename: 'CoreFieldChoiceObject',
                },
              ],
            },
          },
        ],
        individualsFiltersBlocks: [
          {
            individualBlockFilters: [
              {
                comparisonMethod: 'RANGE',
                arguments: [7, 15],
                fieldName: 'age',
                isFlexField: false,
                fieldAttribute: {
                  labelEn: 'Age (calculated)',
                  type: 'INTEGER',
                  choices: null,
                },
              },
              {
                comparisonMethod: 'EQUALS',
                arguments: ['MALE'],
                fieldName: 'sex',
                isFlexField: false,
                fieldAttribute: {
                  labelEn: 'Gender',
                  type: 'SELECT_ONE',
                  choices: [
                    {
                      labels: [
                        {
                          label: 'Female',
                          language: 'English(EN)',
                          __typename: 'LabelNode',
                        },
                      ],
                      labelEn: 'Female',
                      value: 'FEMALE',
                      admin: null,
                      listName: null,
                      __typename: 'CoreFieldChoiceObject',
                    },
                    {
                      labels: [
                        {
                          label: 'Male',
                          language: 'English(EN)',
                          __typename: 'LabelNode',
                        },
                      ],
                      labelEn: 'Male',
                      value: 'MALE',
                      admin: null,
                      listName: null,
                      __typename: 'CoreFieldChoiceObject',
                    },
                  ],
                },
              },
            ],
          },
        ],
      },
    ],
    approvalProcess: {
      totalCount: 1,
      edgeCount: 1,
      edges: [
        {
          node: {
            id: 'testowe',
            sentForAuthorizationDate: '2023-10-02T12:12:12.000000+00:00',
            sentForAuthorizationBy: null,
            sentForReleaseDate: null,
            sentForReleaseBy: null,
            authorizationNumberRequired: 1,
            releaseNumberRequired: 1,
            rejectedOn: null,
            actions: {
              authorization: [],
              release: [],
              reject: [],
            },
          },
        },
      ],
    },
  },
  {
    id: 'PI-946/13',
    unicefId: 'PI-946/13',
    status: 'PENDING',
    deliveryMechanism: 'Transfer to Account',
    fsp: 'CityGroup',
    criteria: [],
    approvalProcess: {
      totalCount: 1,
      edgeCount: 1,
      edges: [],
    },
  },
];

export const ManagePaymentInstructionsPage = (): React.ReactElement => {
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const [items, setItems] = useState<object>(
    initialItems.reduce((a, b) => ({ ...a, [b.id]: b }), {}),
  );

  const buttons = <Box display='flex' justifyContent='center' />;

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_SET_UP_PAYMENT_INSTRUCTIONS, permissions))
    return <PermissionDenied />;

  const actionHandlers = (item) => {
    return {
      handleReject: () => {
        setItems((prevState) => ({
          ...prevState,
          [item.id]: { ...item, status: 'REJECTED' },
        }));
      },
      handleAuthorize: () => {
        setItems((prevState) => ({
          ...prevState,
          [item.id]: { ...item, status: 'AUTHORIZED' },
        }));
      },
      handleRelease: () => {
        setItems((prevState) => ({
          ...prevState,
          [item.id]: { ...item, status: 'RELEASED' },
        }));
      },
    };
  };

  return (
    <>
      <ManagePaymentInstructionsHeader
        baseUrl={baseUrl}
        permissions={permissions}
        buttons={buttons}
      />
      <div>
        {Object.values(items).map((item) => (
          <PaymentInstructionItem
            item={item}
            key={item.id}
            actions={actionHandlers(item)}
          />
        ))}
      </div>
    </>
  );
};
