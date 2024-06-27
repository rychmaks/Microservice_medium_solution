"""This module contains all constants needed for adjustment service."""

DEFAULT_SERVICE_NAME = "rfadjustments"
KEYSPACE_PREFIX = "rfadjustments"
COMMON_DB = "rfadjustments"
REDIS_SERVICE_PATH = "/msp/sessioncache/redis"
ZOOKEEPER_SERVICE_PATH = "/msp/serviceregistry/zookeeper"
KAFKA_SERVICE_PATH = "/msp/messagequeue/kafka"
CLIENT_SERVICE_NAME = "app_clients"
NOTIFICATION_TOPIC = "rfadjustments_events"
SYSTEM_EVENT_TIER_OVERRIDE = 'tier_override'
SYSTEM_EVENT_AMOUNT_OVERRIDE = 'amount_override'

# SDA discovery related
DISCOVER_RETRY_NUM = 3
DISCOVER_RETRY_TIMEOUT = 61

# Workflow related
WORKFLOW_STEP_ANALYST_REVIEW = 'analyst_review'
WORKFLOW_SUBSTEP_ADJUSTMENTS = 'adjustments'


RF_SYSTEM_EVENTS = "rebatesandfees.rfworkflow.system_events"
RF_ADJUSTMENTS_GROUP = "rebatesandfees.rfadjustments.group"

KAFKA_CONSUME_TOPICS = (RF_SYSTEM_EVENTS,)

ADJUSTMENT_UPDATED_TOPIC = "rebatesandfees.rfproject.project_override_changes_channel"

SB_QUALIFICATION_METHODOLOGY_TYPE_REBATE = 'logic_qualification_rebate'
SB_QUALIFICATION_METHODOLOGY_TYPE_PBID = 'logic_qualification_pbid'

DEFAULT_ENGINE_NAME = 'default'
