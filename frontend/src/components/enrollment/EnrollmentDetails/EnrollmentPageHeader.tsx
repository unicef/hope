import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { PageHeader } from '../../../components/core/PageHeader';
import { StatusBox } from '../../../components/core/StatusBox';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { enrollmentBuildStatusToColor } from '../../../utils/utils';
import {
  TargetPopulationBuildStatus,
  TargetPopulationQuery,
  TargetPopulationStatus,
} from '../../../__generated__/graphql';
import { EnrolledEnrollementHeaderButtons } from './EnrolledEnrollementHeaderButtons';
import { LockedEnrollmentHeaderButtons } from './LockedEnrollmentHeaderButtons';
import { OpenEnrollmentHeaderButtons } from './OpenEnrollmentHeaderButtons';

export interface EnrollmentPageHeaderProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  canEdit: boolean;
  canRemove: boolean;
  canDuplicate: boolean;
  canLock: boolean;
  canUnlock: boolean;
}

export const EnrollmentPageHeader = ({
  targetPopulation,
  canEdit,
  canRemove,
  canDuplicate,
  canLock,
  canUnlock,
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
          <Box
            display='flex'
            alignItems='center'
            justify-content='center'
            ml={3}
          >
            {t(`${targetPopulation.name}`)}
            {targetPopulation.buildStatus !==
              TargetPopulationBuildStatus.Ok && (
              <StatusBox
                status={targetPopulation.buildStatus}
                statusToColor={enrollmentBuildStatusToColor}
              />
            )}
          </Box>
        }
        breadCrumbs={breadCrumbsItems}
      >
        {buttons}
      </PageHeader>
    </>
  );
};
