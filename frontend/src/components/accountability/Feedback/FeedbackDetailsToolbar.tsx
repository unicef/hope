import { Box } from '@mui/material';
import EditIcon from '@mui/icons-material/EditRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useHistory, useParams } from 'react-router-dom';
import { FeedbackQuery } from '../../../__generated__/graphql';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { PageHeader } from '../../core/PageHeader';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { ButtonTooltip } from '../../core/ButtonTooltip';
import { useProgramContext } from '../../../programContext';

interface FeedbackDetailsToolbarProps {
  feedback: FeedbackQuery['feedback'];
  canEdit: boolean;
}

export const FeedbackDetailsToolbar = ({
  feedback,
  canEdit,
}: FeedbackDetailsToolbarProps): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const { baseUrl } = useBaseUrl();
  const history = useHistory();
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
              title={t('Program has to be active to edit a Feedback')}
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
                history.push({
                  pathname: `/${baseUrl}/grievance/new-ticket`,
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
                'Program has to be active to create a Linked Ticket to Feedback',
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
};
