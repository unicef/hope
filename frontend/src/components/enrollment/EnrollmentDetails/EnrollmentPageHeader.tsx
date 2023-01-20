import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { PageHeader } from '../../../components/core/PageHeader';
import { StatusBox } from '../../../components/core/StatusBox';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  enrollmentBuildStatusToColor,
  targetPopulationBuildStatusToColor,
} from '../../../utils/utils';
import {
  TargetPopulationBuildStatus,
  TargetPopulationQuery,
  TargetPopulationStatus,
} from '../../../__generated__/graphql';
import { EnrolledEnrollementHeaderButtons } from './EnrolledEnrollementHeaderButtons';
import { FinalizedTargetPopulationHeaderButtons } from './FinalizedTargetPopulationHeaderButtons';
import { LockedEnrollmentHeaderButtons } from './LockedEnrollmentHeaderButtons';
import { LockedTargetPopulationHeaderButtons } from './LockedTargetPopulationHeaderButtons';
import { OpenEnrollmentHeaderButtons } from './OpenEnrollmentHeaderButtons';
import { OpenTargetPopulationHeaderButtons } from './OpenTargetPopulationHeaderButtons';

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
  display: flex;
  flex-direction: row;
`;

export interface EnrollmentPageHeaderProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  canEdit: boolean;
  canRemove: boolean;
  canDuplicate: boolean;
  canLock: boolean;
  canUnlock: boolean;
  canSend: boolean;
}

export const EnrollmentPageHeader = ({
  targetPopulation,
  canEdit,
  canRemove,
  canDuplicate,
  canLock,
  canUnlock,
  canSend,
}: EnrollmentPageHeaderProps): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Enrollment',
      to: `/${businessArea}/enrollment/`,
    },
  ];

  let buttons;

  switch (targetPopulation.status) {
    case TargetPopulationStatus.Open:
      buttons = (
        <OpenEnrollmentHeaderButtons
          targetPopulation={targetPopulation}
          canDuplicate={canDuplicate}
          canRemove={canRemove}
          canEdit={canEdit}
          canLock={canLock}
        />
      );
      break;
    case TargetPopulationStatus.Locked:
      buttons = (
        <LockedEnrollmentHeaderButtons
          targetPopulation={targetPopulation}
          canDuplicate={canDuplicate}
          canUnlock={canUnlock}
          canSend={canSend}
        />
      );
      break;
    default:
      buttons = (
        <EnrolledEnrollementHeaderButtons
          targetPopulation={targetPopulation}
          canDuplicate={canDuplicate}
        />
      );
      break;
  }
  return (
    <>
      <PageHeader
        title={
          <HeaderWrapper>
            {t(`${targetPopulation.name}`)}
            {targetPopulation.buildStatus !==
              TargetPopulationBuildStatus.Ok && (
              <StatusWrapper>
                <StatusBox
                  status={targetPopulation.buildStatus}
                  statusToColor={enrollmentBuildStatusToColor}
                />
              </StatusWrapper>
            )}
          </HeaderWrapper>
        }
        breadCrumbs={breadCrumbsItems}
      >
        {buttons}
      </PageHeader>
    </>
  );
};
