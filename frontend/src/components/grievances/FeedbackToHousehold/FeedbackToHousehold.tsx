import React, { useEffect, useState } from 'react';
import {
  Box,
  Checkbox,
  FormControlLabel,
  Grid,
  Typography,
} from '@material-ui/core';
import { Formik } from 'formik';
import * as Yup from 'yup';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { Title } from '../../core/Title';
import { OverviewContainerColumn } from '../../core/OverviewContainerColumn';
import {
  FeedbackToHouseholdKind,
  GrievanceTicketDocument,
  useAllFeedbackToHouseholdQuery,
  useApproveComplaintMutation,
  useCreateTicketFeedbackToHouseholdMutation,
} from '../../../__generated__/graphql';
import { decodeIdString } from '../../../utils/utils';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { StyledBox } from './styled';
import { MessageInput } from './MessageInput';
import { Message } from './Message';

// const messages = [
//   {
//     id: '1',
//     message: 'lorem lorem lorem lorem lorem lorem lorem lorem lorem ',
//     createdAt: '2020-07-15T16:46:45.166821+00:00',
//     createdBy: {
//       firstName: 'Martin',
//       lastName: 'Scott',
//     },
//     individual: null,
//     kind: FeedbackToHouseholdKind.Message,
//   },
//   {
//     id: '2',
//     message: 'ipsum ipsum ipsum ipsum ipsum ipsum ipsum ipsum ipsum ',
//     createdAt: '2020-07-15T18:32:45.166821+00:00',
//     createdBy: null,
//     individual: {
//       givenName: 'Lani',
//       familyName: 'Olemi',
//       fullName: null,
//     },
//     kind: FeedbackToHouseholdKind.Response,
//   },
// ];

export function FeedbackToHousehold(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const { showMessage } = useSnackbar();
  const [messages, setMessages] = useState([]);
  const [accepted, setAccepted] = useState(false);
  const [mutate, { loading }] = useCreateTicketFeedbackToHouseholdMutation();
  const [approveMutate] = useApproveComplaintMutation();
  const { data, loading: loadingMessages } = useAllFeedbackToHouseholdQuery({
    variables: {
      ticket: decodeIdString(id) || '294cfa7e-b16f-4331-8014-a22ffb2b8b3c',
    },
    fetchPolicy: 'cache-and-network',
  });

  useEffect(() => {
    if (data?.allFeedbackToHousehold) {
      const newMessages = data.allFeedbackToHousehold.edges.map(
        ({ node }) => node,
      );
      setMessages(newMessages);
    }
  }, [data]);

  const initialValues = {
    message: '',
  };

  const validationSchema = Yup.object().shape({
    message: Yup.string().required(t('Message cannot be empty')),
  });

  const renderMessages = (): JSX.Element[] => {
    return messages.map((message) => (
      <Message key={message.id} message={message} />
    ));
  };

  const renderAcceptedByHousehold = (): React.ReactElement => {
    const householdResponded = messages.some(
      (message) => message.kind === FeedbackToHouseholdKind.Response,
    );

    if (!householdResponded) {
      return null;
    }

    if (loadingMessages) return null;

    return (
      <Grid container>
        <Grid item xs={12}>
          <Box mt={2} display='flex' justifyContent='flex-start'>
            <FormControlLabel
              control={
                <Checkbox
                  color='primary'
                  checked={accepted}
                  onChange={(e) => {
                    approveMutate({
                      variables: {
                        grievanceTicketId: id,
                        approveStatus: e.target.checked,
                      },
                      refetchQueries: () => [
                        { query: GrievanceTicketDocument, variables: { id } },
                      ],
                    });
                    setAccepted(e.target.checked);
                  }}
                />
              }
              label={t('Feedback Accepted by household')}
            />
          </Box>
        </Grid>
      </Grid>
    );
  };

  const renderMessageInput = (submitForm): React.ReactElement => {
    if (!accepted) {
      return <MessageInput loading={loading} submitForm={submitForm} />;
    }
    return null;
  };

  return (
    <Grid item xs={8}>
      <Box p={3}>
        <Formik
          initialValues={initialValues}
          onSubmit={async (values, { resetForm }) => {
            try {
              const response = await mutate({
                variables: {
                  feedback: {
                    ticket: id,
                    message: values.message,
                  },
                },
              });
              const newMessage =
                response.data.createFeedbackToHousehold.feedbackToHousehold;
              setMessages((oldMessages) => [...oldMessages, newMessage]);
              resetForm();
            } catch (e) {
              e.graphQLErrors.map((x) => showMessage(x.message));
            }
          }}
          validationSchema={validationSchema}
        >
          {({ submitForm }) => (
            <StyledBox>
              <Title>
                <Typography variant='h6'>
                  {t('Feedback to Household')}
                </Typography>
              </Title>
              <OverviewContainerColumn>
                {renderMessages()}
                {renderAcceptedByHousehold()}
                {renderMessageInput(submitForm)}
              </OverviewContainerColumn>
            </StyledBox>
          )}
        </Formik>
      </Box>
    </Grid>
  );
}
