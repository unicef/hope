import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { ProgramDetails } from '@components/programs/ProgramDetails/ProgramDetails';
import ProgramCyclesTableProgramDetails from '@containers/tables/ProgramCycle/ProgramCyclesTableProgramDetails';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { BusinessArea } from '@restgenerated/models/BusinessArea';
import { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { ProgramStatusEnum } from '@restgenerated/models/ProgramStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { ProgramDetailsPageHeader } from '../headers/ProgramDetailsPageHeader';
import { ApiError } from '@restgenerated/core/ApiError';
import { NotFoundError } from '@utils/errors';

const Container = styled.div`
  && {
    display: flex;
    flex-direction: column;
    min-width: 100%;
  }
`;

const TableWrapper = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  padding: 20px 20px 0;
`;

const NoCashPlansContainer = styled.div`
  margin-top: 120px;
`;
const NoCashPlansTitle = styled.div`
  color: rgba(0, 0, 0, 0.38);
  font-size: 24px;
  line-height: 28px;
  text-align: center;
`;

function ProgramDetailsPage(): ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const { businessArea } = useBaseUrl();
  const navigate = useNavigate();

  const {
    data: program,
    isLoading: loading,
    error,
  } = useQuery<ProgramDetail>({
    queryKey: ['program', businessArea, id],
    queryFn: async () => {
      try {
        return await RestService.restBusinessAreasProgramsRetrieve({
          businessAreaSlug: businessArea,
          slug: id,
        });
      } catch (err) {
        if (err instanceof ApiError && err.status === 404) {
          throw new NotFoundError(
            `Program "${id}" not found in "${businessArea}"`,
          );
        }
        throw err;
      }
    },
    retry: false,
  });

  const { data: businessAreaData, isLoading: businessAreaDataLoading } =
    useQuery<BusinessArea>({
      queryKey: ['businessArea', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasRetrieve({
          slug: businessArea,
        }),
    });

  const { data: choices, isLoading: choicesLoading } = useQuery<ProgramChoices>(
    {
      queryKey: ['programChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasProgramsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
      staleTime: 1000 * 60 * 10,
      gcTime: 1000 * 60 * 30,
    },
  );
  const permissions = usePermissions();

  useEffect(() => {
    if (error instanceof NotFoundError) {
      navigate('/404');
    }
  }, [error, navigate]);

  if (loading || choicesLoading || businessAreaDataLoading)
    return <LoadingComponent />;

  if (isPermissionDeniedError(error))
    return (
      <PermissionDenied
        permission={PERMISSIONS.PROGRAMME_VIEW_LIST_AND_DETAILS}
      />
    );

  if (error) return null;

  if (!choices || !businessAreaData || permissions === null) return null;

  const canFinish = hasPermissions(PERMISSIONS.PROGRAMME_FINISH, permissions);
  return (
    <>
      <ProgramDetailsPageHeader
        program={program}
        canActivate={hasPermissions(
          PERMISSIONS.PROGRAMME_ACTIVATE,
          permissions,
        )}
        canEdit={hasPermissions(PERMISSIONS.PROGRAMME_UPDATE, permissions)}
        canRemove={hasPermissions(PERMISSIONS.PROGRAMME_REMOVE, permissions)}
        canFinish={canFinish}
        canDuplicate={hasPermissions(
          PERMISSIONS.PROGRAMME_DUPLICATE,
          permissions,
        )}
      />
      <Container>
        <ProgramDetails program={program} choices={choices} />
        {program?.status === ProgramStatusEnum.DRAFT ? (
          <NoCashPlansContainer>
            <NoCashPlansTitle>
              {t('Activate the Programme to create a Cycle')}
            </NoCashPlansTitle>
          </NoCashPlansContainer>
        ) : (
          <TableWrapper>
            <ProgramCyclesTableProgramDetails program={program} />
          </TableWrapper>
        )}
        {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
          <UniversalActivityLogTable objectId={program.id} />
        )}
      </Container>
    </>
  );
}

export default ProgramDetailsPage;
