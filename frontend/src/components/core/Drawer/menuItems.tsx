import { Assessment } from '@mui/icons-material';
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
  scopes: string[];
  isSocialWorker?: boolean
};
export const SCOPE_PROGRAM = 'SCOPE_PROGRAM';
export const SCOPE_ALL_PROGRAMS = 'SCOPE_ALL_PROGRAMS';


export const menuItems: MenuItem[] = [
  {
    name: 'Country Dashboard',
    href: '/country-dashboard',
    selectedRegexp: /^\/$/,
    icon: <DashboardIcon />,
    permissions: [PERMISSIONS.DASHBOARD_VIEW_COUNTRY],
    scopes: [SCOPE_ALL_PROGRAMS],
  },
  {
    name: 'Registration Data Import',
    href: '/registration-data-import',
    selectedRegexp: /^\/registration-data-import.*$/,
    icon: <AutorenewIcon />,
    isSocialWorker: false,
    permissions: [PERMISSIONS.RDI_VIEW_DETAILS, PERMISSIONS.RDI_VIEW_LIST],
    scopes: [SCOPE_PROGRAM],
  },
  {
    name: 'Registration Data Import',
    href: '/registration-data-import-for-people',
    selectedRegexp: /^\/registration-data-import.*$/,
    icon: <AutorenewIcon />,
    isSocialWorker: true,
    permissions: [PERMISSIONS.RDI_VIEW_DETAILS, PERMISSIONS.RDI_VIEW_LIST],
    scopes: [SCOPE_PROGRAM],
  },
  {
    name: 'Program Population',
    href: '/population/household',
    selectedRegexp: /^\/population.*$/,
    icon: <PeopleIcon />,
    collapsable: true,
    permissionModule: 'POPULATION',
    scopes: [SCOPE_PROGRAM],
    isSocialWorker: false,
    secondaryActions: [
      {
        name: 'Households',
        href: '/population/household',
        selectedRegexp: /^\/population\/household.*$/,
        icon: <PeopleAltRoundedIcon />,
        permissionModule: 'HOUSEHOLDS',
        scopes: [SCOPE_PROGRAM],
      },
      {
        name: 'Individuals',
        href: '/population/individuals',
        selectedRegexp: /^\/population\/individuals.*$/,
        icon: <FaceIcon />,
        permissionModule: 'INDIVIDUALS',
        scopes: [SCOPE_PROGRAM],
      },
    ],
  },
  {
    name: 'People',
    href: '/population/people',
    selectedRegexp: /^\/population\/people.*$/,
    icon: <PeopleIcon />,
    permissionModule: 'POPULATION',
    scopes: [SCOPE_PROGRAM],
    isSocialWorker: true,
  },
  {
    name: 'Programs',
    href: '/list',
    selectedRegexp: /^\/programs.*$/,
    icon: <Assignment />,
    scopes: [SCOPE_ALL_PROGRAMS],
    permissions: [
      PERMISSIONS.PROGRAMME_MANAGEMENT_VIEW,
      PERMISSIONS.PROGRAMME_VIEW_LIST_AND_DETAILS,
      PERMISSIONS.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
    ],
  },
  {
    name: 'Program Details',
    href: '/programs',
    selectedRegexp: /^\/programs.*$/,
    icon: <Assignment />,
    scopes: [SCOPE_PROGRAM],
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
    scopes: [SCOPE_PROGRAM],
    permissions: [
      PERMISSIONS.TARGETING_VIEW_LIST,
      PERMISSIONS.TARGETING_VIEW_DETAILS,
    ],
  },
  {
    name: 'Payment Module',
    href: '/payment-module',
    selectedRegexp: /^\/payment-module.*$/,
    icon: <PaymentIcon />,
    scopes: [SCOPE_PROGRAM],
    permissions: [PERMISSIONS.PM_VIEW_LIST, PERMISSIONS.PM_VIEW_DETAILS],
    flag: 'isPaymentPlanApplicable',
  },
  {
    name: 'Payment Verification',
    href: '/payment-verification',
    selectedRegexp: /^\/payment-verification.*$/,
    icon: <AttachMoney />,
    scopes: [SCOPE_PROGRAM],
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
    scopes: [SCOPE_PROGRAM, SCOPE_ALL_PROGRAMS],
    secondaryActions: [
      {
        name: 'Grievance Tickets',
        href: '/grievance/tickets/user-generated',
        selectedRegexp: /^\/grievance\/tickets.*$/,
        icon: <ListIcon />,
        permissionModule: 'GRIEVANCES',
        scopes: [SCOPE_PROGRAM, SCOPE_ALL_PROGRAMS],
      },
      {
        name: 'Grievance Dashboard',
        href: '/grievance/dashboard',
        selectedRegexp: /^\/grievance\/dashboard.*$/,
        icon: <Assessment />,
        permissionModule: 'GRIEVANCES',
        scopes: [SCOPE_PROGRAM, SCOPE_ALL_PROGRAMS],
      },
      {
        name: 'Feedback',
        href: '/grievance/feedback',
        selectedRegexp: /^\/grievance\/feedback.*$/,
        icon: <RateReviewIcon />,
        permissionModule: 'GRIEVANCES',
        scopes: [SCOPE_PROGRAM, SCOPE_ALL_PROGRAMS],
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
    scopes: [SCOPE_PROGRAM],
    secondaryActions: [
      {
        name: 'Communication',
        href: '/accountability/communication',
        selectedRegexp: /^\/accountability\/communication.*$/,
        icon: <MessageIcon />,
        permissionModule: 'COMMUNICATION_MESSAGE',
        scopes: [SCOPE_PROGRAM],
      },
      {
        name: 'Surveys',
        href: '/accountability/surveys',
        selectedRegexp: /^\/accountability\/surveys.*$/,
        icon: <BallotIcon />,
        permissionModule: 'SURVEY',
        scopes: [SCOPE_PROGRAM],
      },
    ],
  },
  {
    name: 'Reporting',
    href: '/reporting',
    selectedRegexp: /^\/reporting.*$/,
    icon: <TrendingUpRoundedIcon />,
    permissions: [PERMISSIONS.REPORTING_EXPORT],
    scopes: [SCOPE_ALL_PROGRAMS],
  },
  {
    name: 'Programme Users',
    href: '/users-list',
    selectedRegexp: /^\/users-list.*$/,
    icon: <SupervisedUserCircle />,
    permissions: [PERMISSIONS.USER_MANAGEMENT_VIEW_LIST],
    scopes: [SCOPE_PROGRAM],
  },
  {
    name: 'Activity Log',
    href: '/activity-log',
    selectedRegexp: /^\/activity-log.*$/,
    icon: <TrackChangesIcon />,
    permissions: [PERMISSIONS.ACTIVITY_LOG_VIEW],
    scopes: [SCOPE_ALL_PROGRAMS],
  },
  {
    name: 'Program Log',
    href: '/activity-log',
    selectedRegexp: /^\/activity-log.*$/,
    icon: <TrackChangesIcon />,
    permissions: [PERMISSIONS.ACTIVITY_LOG_VIEW],
    scopes: [SCOPE_PROGRAM],
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
