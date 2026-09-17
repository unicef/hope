import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import CommentIcon from '@mui/icons-material/Comment';
import { UniversalMoment } from '@core/UniversalMoment';

interface SentBackCommentProps {
  comment: string;
  date: string; // ISO string or formatted date
  author: string;
}

const SentBackComment: React.FC<SentBackCommentProps> = ({
  comment,
  date,
  author,
}) => {
  return (
    <Box
      sx={{
        background: '#FFF3EC',
        borderRadius: 3,
        p: 2.5,
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        mb: 2,
        maxWidth: 900,
        minHeight: 64,
      }}
      data-testid="sent-back-comment"
    >
      <Box sx={{ display: 'flex', alignItems: 'center', height: '100%' }}>
        <CommentIcon sx={{ color: '#F2994A', fontSize: 32 }} />
      </Box>
      <Box>
        <Typography
          variant="subtitle1"
          sx={{ color: '#7B5E3B', fontWeight: 600 }}
        >
          Sent Back Comment |{' '}
          <UniversalMoment withTime>{date}</UniversalMoment> | {author}
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 700, mt: 0.5 }}>
          {comment}
        </Typography>
      </Box>
    </Box>
  );
};

export default SentBackComment;
