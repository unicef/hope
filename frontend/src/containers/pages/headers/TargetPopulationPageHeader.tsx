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
import { ApprovedTargetPopulationHeaderButtons } from './ApprovedTargetPopulationHeaderButtons';
import { StatusBox } from '../../../components/StatusBox';
import { targetPopulationStatusToColor } from '../../../utils/utils';

const HeaderWrapper = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  div {
    margin: 0 0 0 ${({ theme }) => theme.spacing(3)}px;
  }
`;
const StatusWrapper = styled.div`
  width: 140px;
`;

export interface ProgramDetailsPageHeaderPropTypes {
  // targetPopulation: TargetPopulationNode;
  isEditMode: boolean;
  setEditState: Function;
  targetPopulation: TargetPopulationNode;
  tabs: React.ReactElement;
}

export function TargetPopulationPageHeader({
  targetPopulation,
  isEditMode,
  setEditState,
  tabs,
}: ProgramDetailsPageHeaderPropTypes): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Targeting',
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
    // case 'IN_PROGRESS': //APPROVED
    //   buttons = (
    //     <ApprovedTargetPopulationHeaderButtons
    //       targetPopulation={targetPopulation}
    //     />
    //   );
    //   break;
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
      buttons = <EditTargetPopulationHeader />;
      break;
  }
  return (
    <>
      <PageHeader
        title={
          <HeaderWrapper>
            {t(`${targetPopulation.name}`)}
            <StatusWrapper>
              <StatusBox
                status={targetPopulation.status}
                statusToColor={targetPopulationStatusToColor}
              />
            </StatusWrapper>
          </HeaderWrapper>
        }
        breadCrumbs={breadCrumbsItems}
        tabs={tabs}
      >
        {buttons}
      </PageHeader>
    </>
  );
}
