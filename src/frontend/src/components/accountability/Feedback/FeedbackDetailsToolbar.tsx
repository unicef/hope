import withErrorBoundary from '@components/core/withErrorBoundary';
import { AdminButton } from '@core/AdminButton';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { ButtonTooltip } from '@core/ButtonTooltip';
import { PageHeader } from '@core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import EditIcon from '@mui/icons-material/EditRounded';
import { Box } from '@mui/material';
import { FeedbackDetail } from '@restgenerated/models/FeedbackDetail';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useProgramContext } from '../../../programContext';

interface FeedbackDetailsToolbarProps {
  feedback: FeedbackDetail;
  canEdit: boolean;
}

function FeedbackDetailsToolbar({
  feedback,
  canEdit,
}: FeedbackDetailsToolbarProps): ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const { baseUrl } = useBaseUrl();
  const navigate = useNavigate();
  const { isActiveProgram } = useProgramContext();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Feedback'),
      to: `/${baseUrl}/grievance/feedback`,
    },
  ];

  const hasLinkedGrievance = Boolean(feedback.linkedGrievanceId);
  const isFeedbackWithHouseholdOnly = Boolean(
    feedback.householdId && !feedback.individualId,
  );

  return (
    <PageHeader
      title={`Feedback ID: ${feedback.unicefId}`}
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={''} />}
      //TODO: Add the correct path for the feedback details page
      // flags={<AdminButton adminUrl={feedback.adminUrl} />}
    >
      <Box display="flex" alignItems="center">
        {canEdit && (
          <Box mr={3}>
            <ButtonTooltip
              color="primary"
              variant="outlined"
              component={Link}
              to={`/${baseUrl}/grievance/feedback/edit-ticket/${id}`}
              startIcon={<EditIcon />}
              data-cy="button-edit"
              title={t('Programme has to be active to edit a Feedback')}
              disabled={!isActiveProgram}
            >
              {t('Edit')}
            </ButtonTooltip>
          </Box>
        )}
        {!hasLinkedGrievance && (
          <Box mr={3}>
            <ButtonTooltip
              onClick={() =>
                navigate(`/${baseUrl}/grievance/new-ticket`, {
                  state: {
                    selectedHousehold: feedback?.householdId,
                    selectedIndividual: feedback?.individualId,
                    linkedFeedbackId: id,
                    isFeedbackWithHouseholdOnly,
                  },
                })
              }
              variant="contained"
              color="primary"
              data-cy="button-create-linked-ticket"
              title={t(
                'Programme has to be active to create a Linked Ticket to Feedback',
              )}
              disabled={!isActiveProgram}
            >
              {t('Create Linked Ticket')}
            </ButtonTooltip>
          </Box>
        )}
      </Box>
    </PageHeader>
  );
}

export default withErrorBoundary(
  FeedbackDetailsToolbar,
  'FeedbackDetailsToolbar',
);
