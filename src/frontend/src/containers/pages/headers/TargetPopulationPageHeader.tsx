import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  TargetPopulationBuildStatus,
  TargetPopulationQuery,
  TargetPopulationStatus,
  useBusinessAreaDataQuery,
} from '@generated/graphql';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { StatusBox } from '@components/core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { targetPopulationBuildStatusToColor } from '@utils/utils';
import { FinalizedTargetPopulationHeaderButtons } from './FinalizedTargetPopulationHeaderButtons';
import { LockedTargetPopulationHeaderButtons } from './LockedTargetPopulationHeaderButtons';
import { OpenTargetPopulationHeaderButtons } from './OpenTargetPopulationHeaderButtons';
import { AdminButton } from '@core/AdminButton';

const HeaderWrapper = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  div {
    margin: 0 0 0 ${({ theme }) => theme.spacing(3)};
  }
`;
const StatusWrapper = styled.div`
  width: 140px;
  display: flex;
  flex-direction: row;
`;

export interface ProgramDetailsPageHeaderPropTypes {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  canEdit: boolean;
  canRemove: boolean;
  canDuplicate: boolean;
  canLock: boolean;
  canUnlock: boolean;
  canSend: boolean;
}

export function TargetPopulationPageHeader({
  targetPopulation,
  canEdit,
  canRemove,
  canDuplicate,
  canLock,
  canUnlock,
  canSend,
}: ProgramDetailsPageHeaderPropTypes): React.ReactElement {
  const { t } = useTranslation();
  const { baseUrl, businessArea } = useBaseUrl();
  const { data: businessAreaData, loading: businessAreaDataLoading } =
    useBusinessAreaDataQuery({
      variables: { businessAreaSlug: businessArea },
    });
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Targeting',
      to: `/${baseUrl}/target-population/`,
    },
  ];

  if (!businessAreaData) return null;
  if (businessAreaDataLoading) return <LoadingComponent />;

  let buttons;

  switch (targetPopulation.status) {
    case TargetPopulationStatus.Open:
      buttons = (
        <OpenTargetPopulationHeaderButtons
          targetPopulation={targetPopulation}
          canDuplicate={canDuplicate}
          canRemove={canRemove}
          canEdit={canEdit}
          canLock={canLock}
        />
      );
      break;
    case TargetPopulationStatus.Locked:
    case TargetPopulationStatus.SteficonCompleted:
    case TargetPopulationStatus.SteficonError:
    case TargetPopulationStatus.SteficonRun:
      buttons = (
        <LockedTargetPopulationHeaderButtons
          targetPopulation={targetPopulation}
          canDuplicate={canDuplicate}
          canUnlock={canUnlock}
          canSend={canSend}
          businessAreaData={businessAreaData}
        />
      );
      break;
    default:
      // Ready for Cash Assist, Processing, Ready, Accepted
      buttons = (
        <FinalizedTargetPopulationHeaderButtons
          targetPopulation={targetPopulation}
          canDuplicate={canDuplicate}
          businessAreaData={businessAreaData}
        />
      );
      break;
  }
  return (
    <PageHeader
      title={
        <HeaderWrapper>
          {t(`${targetPopulation.name}`)}
          {targetPopulation.buildStatus !== TargetPopulationBuildStatus.Ok && (
            <StatusWrapper>
              <StatusBox
                status={targetPopulation.buildStatus}
                statusToColor={targetPopulationBuildStatusToColor}
              />
            </StatusWrapper>
          )}
        </HeaderWrapper>
      }
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={targetPopulation.adminUrl} />}
    >
      {buttons}
    </PageHeader>
  );
}
