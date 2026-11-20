import type { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { StatusBox } from '@components/core/StatusBox';
import { AdminButton } from '@core/AdminButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { BusinessArea } from '@restgenerated/models/BusinessArea';
import { PaymentListStatusEnum } from '@restgenerated/models/PaymentListStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { useQuery } from '@tanstack/react-query';
import { paymentListBuildStatusToColor } from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FinalizedTargetPopulationHeaderButtons } from './FinalizedTargetPopulationHeaderButtons';
import { LockedTargetPopulationHeaderButtons } from './LockedTargetPopulationHeaderButtons';
import { OpenTargetPopulationHeaderButtons } from './OpenTargetPopulationHeaderButtons';
import type { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';

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
  paymentList: TargetPopulationDetail;
  canEdit: boolean;
  canRemove: boolean;
  canDuplicate: boolean;
  canLock: boolean;
  canUnlock: boolean;
  canSend: boolean;
}

export function TargetPopulationPageHeader({
  paymentList,
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
      queryKey: restQueryKey(RestService.restBusinessAreasRetrieve, {
        slug: businessArea,
      }),
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

  switch (paymentList.status) {
    case PaymentListStatusEnum.TP_OPEN:
      buttons = (
        <OpenTargetPopulationHeaderButtons
          targetPopulation={paymentList}
          canDuplicate={canDuplicate}
          canRemove={canRemove}
          canEdit={canEdit}
          canLock={canLock}
        />
      );
      break;
    case PaymentListStatusEnum.TP_LOCKED:
    case PaymentListStatusEnum.STEFICON_COMPLETED:
    case PaymentListStatusEnum.STEFICON_ERROR:
    case PaymentListStatusEnum.STEFICON_RUN:
      buttons = (
        <LockedTargetPopulationHeaderButtons
          targetPopulation={paymentList}
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
          targetPopulation={paymentList}
          canDuplicate={canDuplicate}
        />
      );
      break;
  }
  return (
    <PageHeader
      title={
        <HeaderWrapper>
          {t(`${paymentList.name}`)}
          {paymentList.buildStatus !== 'OK' && (
            <StatusWrapper>
              <StatusBox
                status={paymentList.buildStatus}
                statusToColor={paymentListBuildStatusToColor}
              />
            </StatusWrapper>
          )}
        </HeaderWrapper>
      }
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={paymentList.adminUrl} />}
    >
      {buttons}
    </PageHeader>
  );
}
