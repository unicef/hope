import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { StatusBox } from '@components/core/StatusBox';
import { AdminButton } from '@core/AdminButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { BusinessArea } from '@restgenerated/models/BusinessArea';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { paymentPlanBuildStatusToColor } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FinalizedTargetPopulationHeaderButtons } from './FinalizedTargetPopulationHeaderButtons';
import { LockedTargetPopulationHeaderButtons } from './LockedTargetPopulationHeaderButtons';
import { OpenTargetPopulationHeaderButtons } from './OpenTargetPopulationHeaderButtons';

const HeaderWrapper = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  div {
    margin: 0 0 0 ${({ theme }) => theme.spacing(3)};
  }
`;
const StatusWrapper = styled.div`
  display: flex;
  flex-direction: row;
`;

export interface TargetPopulationPageHeaderProps {
  paymentPlan;
  canEdit: boolean;
  canRemove: boolean;
  canDuplicate: boolean;
  canLock: boolean;
  canUnlock: boolean;
  canSend: boolean;
}

export function TargetPopulationPageHeader({
  paymentPlan,
  canEdit,
  canRemove,
  canDuplicate,
  canLock,
  canUnlock,
  canSend,
}: TargetPopulationPageHeaderProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl, businessArea } = useBaseUrl();
  const { data: businessAreaData, isLoading: businessAreaDataLoading } =
    useQuery<BusinessArea>({
      queryKey: ['businessArea', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasRetrieve({
          slug: businessArea,
        }),
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

  switch (paymentPlan.status) {
    case PaymentPlanStatusEnum.OPEN:
      buttons = (
        <OpenTargetPopulationHeaderButtons
          targetPopulation={paymentPlan}
          canDuplicate={canDuplicate}
          canRemove={canRemove}
          canEdit={canEdit}
          canLock={canLock}
        />
      );
      break;
    case PaymentPlanStatusEnum.TP_LOCKED:
    case PaymentPlanStatusEnum.STEFICON_COMPLETED:
    case PaymentPlanStatusEnum.STEFICON_ERROR:
    case PaymentPlanStatusEnum.STEFICON_RUN:
      buttons = (
        <LockedTargetPopulationHeaderButtons
          targetPopulation={paymentPlan}
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
          targetPopulation={paymentPlan}
          canDuplicate={canDuplicate}
        />
      );
      break;
  }
  return (
    <PageHeader
      title={
        <HeaderWrapper>
          {t(`${paymentPlan.name}`)}
          {paymentPlan.buildStatus !== 'OK' && (
            <StatusWrapper>
              <StatusBox
                status={paymentPlan.buildStatus}
                statusToColor={paymentPlanBuildStatusToColor}
              />
            </StatusWrapper>
          )}
        </HeaderWrapper>
      }
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={paymentPlan.adminUrl} />}
    >
      {buttons}
    </PageHeader>
  );
}
