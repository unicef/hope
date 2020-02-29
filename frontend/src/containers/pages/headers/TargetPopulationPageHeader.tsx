import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Button } from '@material-ui/core';
import { EditRounded } from '@material-ui/icons';
import { TargetPopulationNode } from '../../../__generated__/graphql';
import { PageHeader } from '../../../components/PageHeader';
import { BreadCrumbsItem } from '../../../components/BreadCrumbs';
import { useBusinessArea } from '../../../hooks/useBusinessArea';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface ProgramDetailsPageHeaderPropTypes {
  // targetPopulation: TargetPopulationNode;
  isEditMode: boolean;
  setEditState: Function;
}

export function TargetPopulationPageHeader({
  // targetPopulation,
  isEditMode,
  setEditState
}: ProgramDetailsPageHeaderPropTypes): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Programme Managment',
      to: `/${businessArea}/target-population/`,
    },
  ];
  return (
    <PageHeader title={t('sample name')} breadCrumbs={breadCrumbsItems}>
      <>
        <ButtonContainer>
          <Button
            variant='outlined'
            color='primary'
            startIcon={<EditRounded />}
            onClick={() => setEditState(!isEditMode)}
          >
            Edit
          </Button>
        </ButtonContainer>
        <ButtonContainer>
          <Button variant='contained' color='primary'>
            Finalize
          </Button>
        </ButtonContainer>
      </>
    </PageHeader>
  );
}
