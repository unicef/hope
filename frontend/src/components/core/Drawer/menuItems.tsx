import { Assessment, ManageAccounts } from '@mui/icons-material';
import Assignment from '@mui/icons-material/Assignment';
import DashboardIcon from '@mui/icons-material/DashboardRounded';
import AttachMoney from '@mui/icons-material/AttachMoney';
import AutorenewIcon from '@mui/icons-material/AutorenewRounded';
import BallotIcon from '@mui/icons-material/Ballot';
import FaceIcon from '@mui/icons-material/Face';
import Feedback from '@mui/icons-material/Feedback';
import ForumIcon from '@mui/icons-material/Forum';
import InfoIcon from '@mui/icons-material/Info';
import ListIcon from '@mui/icons-material/List';
import ListAltRoundedIcon from '@mui/icons-material/ListAltRounded';
import LocalLibrary from '@mui/icons-material/LocalLibrary';
import MessageIcon from '@mui/icons-material/Message';
import NewReleases from '@mui/icons-material/NewReleases';
import PaymentIcon from '@mui/icons-material/Payment';
import PeopleAltRoundedIcon from '@mui/icons-material/PeopleAltRounded';
import PeopleIcon from '@mui/icons-material/PeopleRounded';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import RateReviewIcon from '@mui/icons-material/RateReview';
import SupervisedUserCircle from '@mui/icons-material/SupervisedUserCircle';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import TrendingUpRoundedIcon from '@mui/icons-material/TrendingUpRounded';
import { PERMISSIONS } from '../../../config/permissions';

export type MenuItem = {
  name: string;
  href?: string;
  selectedRegexp: RegExp;
  icon: JSX.Element;
  permissions?: string[];
  collapsable?: boolean;
  permissionModule?: string;
  secondaryActions?: MenuItem[];
  flag?: string;
  external?: boolean;
};
export const menuItems: MenuItem[] = [
  {
    name: 'Country Dashboard',
    href: '/country-dashboard',
    selectedRegexp: /^\/$/,
    icon: <DashboardIcon />,
    permissions: [PERMISSIONS.DASHBOARD_VIEW_COUNTRY],
  },
  {
    name: 'Registration Data Import',
    href: '/registration-data-import',
    selectedRegexp: /^\/registration-data-import.*$/,
    icon: <AutorenewIcon />,
    permissions: [PERMISSIONS.RDI_VIEW_DETAILS, PERMISSIONS.RDI_VIEW_LIST],
  },
  {
    name: 'Programme Population',
    href: '/population/household',
    selectedRegexp: /^\/population.*$/,
    icon: <PeopleIcon />,
    collapsable: true,
    permissionModule: 'POPULATION',
    secondaryActions: [
      {
        name: 'Households',
        href: '/population/household',
        selectedRegexp: /^\/population\/household.*$/,
        icon: <PeopleAltRoundedIcon />,
        permissionModule: 'HOUSEHOLDS',
      },
      {
        name: 'Individuals',
        href: '/population/individuals',
        selectedRegexp: /^\/population\/individuals.*$/,
        icon: <FaceIcon />,
        permissionModule: 'INDIVIDUALS',
      },
    ],
  },
  {
    name: 'Programme Management',
    href: '/list',
    selectedRegexp: /^\/programs.*$/,
    icon: <Assignment />,
    permissions: [
      PERMISSIONS.PROGRAMME_MANAGEMENT_VIEW,
      PERMISSIONS.PROGRAMME_VIEW_LIST_AND_DETAILS,
      PERMISSIONS.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
    ],
  },
  {
    name: 'Managerial Console',
    href: '/managerial-console',
    selectedRegexp: /^\/managerial-console.*$/,
    icon: <ManageAccounts />,
    permissions: [PERMISSIONS.PAYMENT_VIEW_LIST_MANAGERIAL],
  },
  {
    name: 'Programme Details',
    href: '/programs',
    selectedRegexp: /^\/programs.*$/,
    icon: <Assignment />,
    permissions: [
      PERMISSIONS.PROGRAMME_VIEW_LIST_AND_DETAILS,
      PERMISSIONS.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
    ],
  },
  {
    name: 'Targeting',
    href: '/target-population',
    selectedRegexp: /^\/target-population.*$/,
    icon: <ListAltRoundedIcon />,
    permissions: [
      PERMISSIONS.TARGETING_VIEW_LIST,
      PERMISSIONS.TARGETING_VIEW_DETAILS,
    ],
  },
  {
    name: 'Cash Assist',
    selectedRegexp: /^\/unique.*$/,
    icon: <PaymentIcon />,
    external: true,
  },
  {
    name: 'Payment Module',
    href: '/payment-module',
    selectedRegexp: /^\/payment-module.*$/,
    icon: <PaymentIcon />,
    permissions: [PERMISSIONS.PM_VIEW_LIST, PERMISSIONS.PM_VIEW_DETAILS],
    flag: 'isPaymentPlanApplicable',
  },
  {
    name: 'Payment Verification',
    href: '/payment-verification',
    selectedRegexp: /^\/payment-verification.*$/,
    icon: <AttachMoney />,
    permissions: [
      PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST,
      PERMISSIONS.PAYMENT_VERIFICATION_VIEW_DETAILS,
      PERMISSIONS.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
    ],
  },
  {
    name: 'Grievance',
    href: '/grievance/tickets',
    selectedRegexp: /^\/grievance\/tickets.*$/,
    icon: <Feedback />,
    collapsable: true,
    permissionModule: 'GRIEVANCES',
    secondaryActions: [
      {
        name: 'Grievance Tickets',
        href: '/grievance/tickets/user-generated',
        selectedRegexp: /^\/grievance\/tickets.*$/,
        icon: <ListIcon />,
        permissionModule: 'GRIEVANCES',
      },
      {
        name: 'Grievance Dashboard',
        href: '/grievance/dashboard',
        selectedRegexp: /^\/grievance\/dashboard.*$/,
        icon: <Assessment />,
        permissionModule: 'GRIEVANCES',
      },
      {
        name: 'Feedback',
        href: '/grievance/feedback',
        selectedRegexp: /^\/grievance\/feedback.*$/,
        icon: <RateReviewIcon />,
        permissionModule: 'GRIEVANCES',
      },
    ],
  },
  {
    name: 'Accountability',
    href: '/accountability/communication',
    selectedRegexp: /^\/accountability\/communication.*$/,
    icon: <ForumIcon />,
    collapsable: true,
    permissionModule: 'ACCOUNTABILITY',
    flag: 'isAccountabilityApplicable',
    secondaryActions: [
      {
        name: 'Communication',
        href: '/accountability/communication',
        selectedRegexp: /^\/accountability\/communication.*$/,
        icon: <MessageIcon />,
        permissionModule: 'COMMUNICATION_MESSAGE',
      },
      {
        name: 'Surveys',
        href: '/accountability/surveys',
        selectedRegexp: /^\/accountability\/surveys.*$/,
        icon: <BallotIcon />,
        permissionModule: 'SURVEY',
      },
    ],
  },
  {
    name: 'Reporting',
    href: '/reporting',
    selectedRegexp: /^\/reporting.*$/,
    icon: <TrendingUpRoundedIcon />,
    permissions: [PERMISSIONS.REPORTING_EXPORT],
  },
  {
    name: 'Programme Users',
    href: '/users-list',
    selectedRegexp: /^\/users-list.*$/,
    icon: <SupervisedUserCircle />,
    permissions: [PERMISSIONS.USER_MANAGEMENT_VIEW_LIST],
  },
  {
    name: 'Activity Log',
    href: '/activity-log',
    selectedRegexp: /^\/activity-log.*$/,
    icon: <TrackChangesIcon />,
    permissions: [PERMISSIONS.ACTIVITY_LOG_VIEW],
  },
];

export const resourcesItems = [
  {
    name: 'Knowledge Base',
    href: 'https://unicef.service-now.com/cc?id=kb_search&kb_knowledge_base=be5501f9db003850d180f264f39619ee',
    icon: <LocalLibrary />,
  },
  {
    name: 'Conversations',
    href: 'https://web.yammer.com/main/groups/eyJfdHlwZSI6Ikdyb3VwIiwiaWQiOiIxMzAzMTkwMDc3NDQifQ/all',
    icon: <QuestionAnswerIcon />,
  },
  {
    name: 'Tools and Materials',
    href: 'https://unicef.sharepoint.com/sites/EMOPS-HOPE',
    icon: <InfoIcon />,
  },
  {
    name: 'Release Note',
    href: '/api/changelog/',
    icon: <NewReleases />,
  },
];
