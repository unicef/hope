import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { TargetPopulationNode } from '../../../__generated__/graphql';
import { PageHeader } from '../../../components/PageHeader';
import { BreadCrumbsItem } from '../../../components/BreadCrumbs';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { InProgressTargetPopulationHeaderButtons } from './InProgressTargetPopulationHeaderButtons';
import { FinalizedTargetPopulationHeaderButtons } from './FinalizedTargetPopulationHeaderButtons';
import { EditTargetPopulationHeader } from './EditTargetPopulationHeader';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface ProgramDetailsPageHeaderPropTypes {
  // targetPopulation: TargetPopulationNode;
  isEditMode: boolean;
  setEditState: Function;
  targetPopulation: TargetPopulationNode;
}

export function TargetPopulationPageHeader({
  targetPopulation,
  isEditMode,
  setEditState,
}: ProgramDetailsPageHeaderPropTypes): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Target Population',
      to: `/${businessArea}/target-population/`,
    },
  ];
  //TODO: Use statuses from node - not in backend yet
  let buttons;
  switch (targetPopulation.status) {
    case 'IN_PROGRESS':
      buttons = (
        <InProgressTargetPopulationHeaderButtons
          targetPopulation={targetPopulation}
          setEditState={setEditState}
        />
      );
      break;
    case 'FINALIZED':
      buttons = (
        <FinalizedTargetPopulationHeaderButtons
          targetPopulation={targetPopulation}
        />
      );
      break;
    default:
      //TODO: this could be edit case, in such scenario 
      //wrap other components in page header
      buttons = (
        <EditTargetPopulationHeader />
      );
      break;
  }
  return (
    <>
      {isEditMode ? (
        <PageHeader title={<div>Edit input</div>}>
          <EditTargetPopulationHeader />
        </PageHeader>
      ) : (
        <PageHeader
          title={t(`${targetPopulation.name}`)}
          breadCrumbs={breadCrumbsItems}
        >
          {buttons}
        </PageHeader>
      )}
    </>
  );
}
