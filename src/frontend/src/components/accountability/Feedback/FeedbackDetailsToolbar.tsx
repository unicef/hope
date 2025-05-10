import { Box } from '@mui/material';
import EditIcon from '@mui/icons-material/EditRounded';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { FeedbackQuery } from '@generated/graphql';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ButtonTooltip } from '@core/ButtonTooltip';
import { useProgramContext } from '../../../programContext';
import { AdminButton } from '@core/AdminButton';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface FeedbackDetailsToolbarProps {
  feedback: FeedbackQuery['feedback'];
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

  const hasLinkedGrievance = Boolean(feedback.linkedGrievance?.id);
  const isFeedbackWithHouseholdOnly = Boolean(
    feedback.householdLookup?.id && !feedback.individualLookup?.id,
  );

  return (
    <PageHeader
      title={`Feedback ID: ${feedback.unicefId}`}
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={feedback.adminUrl} />}
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
                    selectedHousehold: feedback?.householdLookup,
                    selectedIndividual: feedback?.individualLookup,
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
