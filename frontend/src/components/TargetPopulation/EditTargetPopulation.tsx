import React from 'react';
import styled from 'styled-components';
import { useParams } from 'react-router-dom';
import { Button } from '@material-ui/core';
import { Formik, Form } from 'formik';
import { PageHeader } from '../PageHeader';
import { BreadCrumbsItem } from '../BreadCrumbs';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import {
  TargetingCriteriaRuleObjectType,
  useUpdateTpMutation,
} from '../../__generated__/graphql';
import { useSnackbar } from '../../hooks/useSnackBar';
import { CandidateListTab } from './Edit/CandidateListTab';
import { TargetPopulationProgramme } from './TargetPopulationProgramme';
import { TARGET_POPULATION_QUERY } from '../../apollo/queries/TargetPopulation';


const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

interface EditTargetPopulationProps {
  targetPopulationCriterias?;
  cancelEdit?;
  targetPopulation?;
}

export function EditTargetPopulation({
  targetPopulationCriterias,
  cancelEdit,
  targetPopulation,
}: EditTargetPopulationProps): React.ReactElement {
  const initialValues = {
    id: targetPopulation.id,
    programmeName: targetPopulation.name || '',
    criterias: targetPopulationCriterias.rules || [],
    candidateListCriterias:
      targetPopulation.candidateListTargetingCriteria?.rules || [],
    targetPopulationCriterias:
      targetPopulation.finalListTargetingCriteria?.rules || [],
  };
  const [mutate] = useUpdateTpMutation();
  const { showMessage } = useSnackbar();
  const { id } = useParams();

  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Targeting',
      to: `/${businessArea}/target-population/`,
    },
  ];

  const isTitleEditable = (): boolean => {
    switch (targetPopulation.status) {
      case 'APPROVED':
        return false;
      default:
        return true;
    }
  };
  const mapRules = (status, values): TargetingCriteriaRuleObjectType[] => {
    switch (status) {
      case 'DRAFT':
        return values.candidateListCriterias.map((rule) => {
          return {
            filters: rule.filters.map((each) => {
              return {
                comparisionMethod: each.comparisionMethod,
                arguments: each.arguments,
                fieldName: each.fieldName,
                isFlexField: each.isFlexField,
                headOfHousehold: each.headOfHousehold,
              };
            }),
          };
        });
      default:
        return values.targetPopulationCriterias.map((rule) => {
          return {
            filters: rule.filters.map((each) => {
              return {
                comparisionMethod: each.comparisionMethod,
                arguments: each.arguments,
                fieldName: each.fieldName,
                isFlexField: each.isFlexField,
                headOfHousehold: each.headOfHousehold,
              };
            }),
          };
        });
    }
  };
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={async (values) => {
        await mutate({
          variables: {
            input: {
              id: values.id,
              ...(targetPopulation.status === 'DRAFT' && { name: values.programmeName }),
              targetingCriteria: {
                rules: mapRules(targetPopulation.status, values),
              },
            },
          },
          refetchQueries: [
            {
              query: TARGET_POPULATION_QUERY,
              variables: {
                id
              },
            },
          ],
        });
        cancelEdit();
        showMessage('Target Population Updated', {
          pathname: `/${businessArea}/target-population/${values.id}`,
          historyMethod: 'push',
        });
      }}
    >
      {({ submitForm, values }) => (
        <Form>
          <PageHeader
            title={values.programmeName}
            breadCrumbs={breadCrumbsItems}
            hasInputComponent
          >
            <>
              {values.programmeName && (
                <ButtonContainer>
                  <Button
                    variant='outlined'
                    color='primary'
                    onClick={cancelEdit}
                  >
                    Cancel
                  </Button>
                </ButtonContainer>
              )}
              <ButtonContainer>
                <Button
                  variant='contained'
                  color='primary'
                  type='submit'
                  onClick={submitForm}
                  disabled={!values.programmeName}
                >
                  Save
                </Button>
              </ButtonContainer>
            </>
          </PageHeader>
          <TargetPopulationProgramme targetPopulation={targetPopulation} />
          <CandidateListTab values={values} />
        </Form>
      )}
    </Formik>
  );
}
