# flake8: noqa
# fmt: off
# mypy: disable-error-code="no-any-return, no-untyped-call, misc, type-arg"
# This file was automatically generated by algokit-client-generator.
# DO NOT MODIFY IT BY HAND.
# requires: algokit-utils@^1.2.0
import base64
import dataclasses
import decimal
import typing
from abc import ABC, abstractmethod

import algokit_utils
import algosdk
from algosdk.v2client import models
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    AtomicTransactionResponse,
    SimulateAtomicTransactionResponse,
    TransactionSigner,
    TransactionWithSigner
)

_APP_SPEC_JSON = r"""{
    "hints": {
        "create()bool": {
            "call_config": {
                "no_op": "ALL"
            }
        },
        "update()bool": {
            "call_config": {
                "update_application": "CALL"
            }
        },
        "delete()bool": {
            "call_config": {
                "delete_application": "CALL"
            }
        },
        "opt_contract_into_asset(asset)bool": {
            "call_config": {
                "no_op": "CALL"
            }
        }
    },
    "source": {
        "approval": "I3ByYWdtYSB2ZXJzaW9uIDEwCgpzbWFydF9jb250cmFjdHMuemFpYmF0c3VfYmFzZS5jb250cmFjdC5aYWliYXRzdUJhc2UuYXBwcm92YWxfcHJvZ3JhbToKICAgIHR4biBBcHBsaWNhdGlvbklECiAgICBibnogbWFpbl9lbnRyeXBvaW50QDIKICAgIGNhbGxzdWIgX19pbml0X18KCm1haW5fZW50cnlwb2ludEAyOgogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6MTEKICAgIC8vIGNsYXNzIFphaWJhdHN1QmFzZShhcC5BUkM0Q29udHJhY3QpOgogICAgbWV0aG9kICJjcmVhdGUoKWJvb2wiCiAgICBtZXRob2QgInVwZGF0ZSgpYm9vbCIKICAgIG1ldGhvZCAiZGVsZXRlKClib29sIgogICAgbWV0aG9kICJvcHRfY29udHJhY3RfaW50b19hc3NldChhc3NldClib29sIgogICAgdHhuYSBBcHBsaWNhdGlvbkFyZ3MgMAogICAgbWF0Y2ggbWFpbl9jcmVhdGVfcm91dGVAMyBtYWluX3VwZGF0ZV9yb3V0ZUA0IG1haW5fZGVsZXRlX3JvdXRlQDUgbWFpbl9vcHRfY29udHJhY3RfaW50b19hc3NldF9yb3V0ZUA2CiAgICBlcnIgLy8gcmVqZWN0IHRyYW5zYWN0aW9uCgptYWluX2NyZWF0ZV9yb3V0ZUAzOgogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6MTYKICAgIC8vIEBhNC5hYmltZXRob2QoY3JlYXRlPSJhbGxvdyIpCiAgICB0eG4gT25Db21wbGV0aW9uCiAgICAhCiAgICBhc3NlcnQgLy8gT25Db21wbGV0aW9uIGlzIE5vT3AKICAgIGNhbGxzdWIgY3JlYXRlCiAgICBieXRlIDB4MDAKICAgIGludCAwCiAgICB1bmNvdmVyIDIKICAgIHNldGJpdAogICAgYnl0ZSAweDE1MWY3Yzc1CiAgICBzd2FwCiAgICBjb25jYXQKICAgIGxvZwogICAgaW50IDEKICAgIHJldHVybgoKbWFpbl91cGRhdGVfcm91dGVANDoKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy96YWliYXRzdV9iYXNlL2NvbnRyYWN0LnB5OjIxCiAgICAvLyBAYTQuYWJpbWV0aG9kKGFsbG93X2FjdGlvbnM9WyJVcGRhdGVBcHBsaWNhdGlvbiJdKQogICAgdHhuIE9uQ29tcGxldGlvbgogICAgaW50IFVwZGF0ZUFwcGxpY2F0aW9uCiAgICA9PQogICAgYXNzZXJ0IC8vIE9uQ29tcGxldGlvbiBpcyBVcGRhdGVBcHBsaWNhdGlvbgogICAgdHhuIEFwcGxpY2F0aW9uSUQKICAgIGFzc2VydCAvLyBpcyBub3QgY3JlYXRpbmcKICAgIGNhbGxzdWIgdXBkYXRlCiAgICBieXRlIDB4MDAKICAgIGludCAwCiAgICB1bmNvdmVyIDIKICAgIHNldGJpdAogICAgYnl0ZSAweDE1MWY3Yzc1CiAgICBzd2FwCiAgICBjb25jYXQKICAgIGxvZwogICAgaW50IDEKICAgIHJldHVybgoKbWFpbl9kZWxldGVfcm91dGVANToKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy96YWliYXRzdV9iYXNlL2NvbnRyYWN0LnB5OjMwCiAgICAvLyBAYTQuYWJpbWV0aG9kKGFsbG93X2FjdGlvbnM9WyJEZWxldGVBcHBsaWNhdGlvbiJdKQogICAgdHhuIE9uQ29tcGxldGlvbgogICAgaW50IERlbGV0ZUFwcGxpY2F0aW9uCiAgICA9PQogICAgYXNzZXJ0IC8vIE9uQ29tcGxldGlvbiBpcyBEZWxldGVBcHBsaWNhdGlvbgogICAgdHhuIEFwcGxpY2F0aW9uSUQKICAgIGFzc2VydCAvLyBpcyBub3QgY3JlYXRpbmcKICAgIGNhbGxzdWIgZGVsZXRlCiAgICBieXRlIDB4MDAKICAgIGludCAwCiAgICB1bmNvdmVyIDIKICAgIHNldGJpdAogICAgYnl0ZSAweDE1MWY3Yzc1CiAgICBzd2FwCiAgICBjb25jYXQKICAgIGxvZwogICAgaW50IDEKICAgIHJldHVybgoKbWFpbl9vcHRfY29udHJhY3RfaW50b19hc3NldF9yb3V0ZUA2OgogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6MzYKICAgIC8vIEBhNC5hYmltZXRob2QoKQogICAgdHhuIE9uQ29tcGxldGlvbgogICAgIQogICAgYXNzZXJ0IC8vIE9uQ29tcGxldGlvbiBpcyBOb09wCiAgICB0eG4gQXBwbGljYXRpb25JRAogICAgYXNzZXJ0IC8vIGlzIG5vdCBjcmVhdGluZwogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6MTEKICAgIC8vIGNsYXNzIFphaWJhdHN1QmFzZShhcC5BUkM0Q29udHJhY3QpOgogICAgdHhuYSBBcHBsaWNhdGlvbkFyZ3MgMQogICAgYnRvaQogICAgdHhuYXMgQXNzZXRzCiAgICAvLyBzbWFydF9jb250cmFjdHMvemFpYmF0c3VfYmFzZS9jb250cmFjdC5weTozNgogICAgLy8gQGE0LmFiaW1ldGhvZCgpCiAgICBjYWxsc3ViIG9wdF9jb250cmFjdF9pbnRvX2Fzc2V0CiAgICBieXRlIDB4MDAKICAgIGludCAwCiAgICB1bmNvdmVyIDIKICAgIHNldGJpdAogICAgYnl0ZSAweDE1MWY3Yzc1CiAgICBzd2FwCiAgICBjb25jYXQKICAgIGxvZwogICAgaW50IDEKICAgIHJldHVybgoKCi8vIHNtYXJ0X2NvbnRyYWN0cy56YWliYXRzdV9iYXNlLmNvbnRyYWN0LlphaWJhdHN1QmFzZS5jcmVhdGUoKSAtPiB1aW50NjQ6CmNyZWF0ZToKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy96YWliYXRzdV9iYXNlL2NvbnRyYWN0LnB5OjE2LTE3CiAgICAvLyBAYTQuYWJpbWV0aG9kKGNyZWF0ZT0iYWxsb3ciKQogICAgLy8gZGVmIGNyZWF0ZShzZWxmKSAtPiBib29sOgogICAgcHJvdG8gMCAxCiAgICAvLyBzbWFydF9jb250cmFjdHMvemFpYmF0c3VfYmFzZS9jb250cmFjdC5weToxOAogICAgLy8gc2VsZi5hZG1pbnMuYXBwZW5kKGE0LkFkZHJlc3MoYXAuVHhuLnNlbmRlcikpCiAgICBpbnQgMAogICAgYnl0ZSAiYWRtaW5zIgogICAgYXBwX2dsb2JhbF9nZXRfZXgKICAgIGFzc2VydCAvLyBjaGVjayBhZG1pbnMgZXhpc3RzCiAgICBleHRyYWN0IDIgMAogICAgdHhuIFNlbmRlcgogICAgY29uY2F0CiAgICBkdXAKICAgIGxlbgogICAgaW50IDMyCiAgICAvCiAgICBpdG9iCiAgICBleHRyYWN0IDYgMAogICAgc3dhcAogICAgY29uY2F0CiAgICBieXRlICJhZG1pbnMiCiAgICBzd2FwCiAgICBhcHBfZ2xvYmFsX3B1dAogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6MTkKICAgIC8vIHJldHVybiBUcnVlCiAgICBpbnQgMQogICAgcmV0c3ViCgoKLy8gc21hcnRfY29udHJhY3RzLnphaWJhdHN1X2Jhc2UuY29udHJhY3QuWmFpYmF0c3VCYXNlLnVwZGF0ZSgpIC0+IHVpbnQ2NDoKdXBkYXRlOgogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6MjEtMjIKICAgIC8vIEBhNC5hYmltZXRob2QoYWxsb3dfYWN0aW9ucz1bIlVwZGF0ZUFwcGxpY2F0aW9uIl0pCiAgICAvLyBkZWYgdXBkYXRlKHNlbGYpIC0+IGJvb2w6CiAgICBwcm90byAwIDEKICAgIGJ5dGUgIiIKICAgIGR1cAogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6MjMKICAgIC8vIGlmIGFwLlR4bi5zZW5kZXIgPT0gb3AuR2xvYmFsLmNyZWF0b3JfYWRkcmVzczoKICAgIHR4biBTZW5kZXIKICAgIGdsb2JhbCBDcmVhdG9yQWRkcmVzcwogICAgPT0KICAgIGJ6IHVwZGF0ZV9hZnRlcl9pZl9lbHNlQDIKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy96YWliYXRzdV9iYXNlL2NvbnRyYWN0LnB5OjI0CiAgICAvLyByZXR1cm4gVHJ1ZQogICAgaW50IDEKICAgIGZyYW1lX2J1cnkgMAogICAgcmV0c3ViCgp1cGRhdGVfYWZ0ZXJfaWZfZWxzZUAyOgogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6MjUKICAgIC8vIGZvciBpbmRleCBpbiBhcC51cmFuZ2Uoc2VsZi5hZG1pbnMubGVuZ3RoKToKICAgIGludCAwCiAgICBieXRlICJhZG1pbnMiCiAgICBhcHBfZ2xvYmFsX2dldF9leAogICAgYXNzZXJ0IC8vIGNoZWNrIGFkbWlucyBleGlzdHMKICAgIGludCAwCiAgICBleHRyYWN0X3VpbnQxNgogICAgZnJhbWVfYnVyeSAxCiAgICBpbnQgMAogICAgZnJhbWVfYnVyeSAwCgp1cGRhdGVfZm9yX2hlYWRlckAzOgogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6MjUKICAgIC8vIGZvciBpbmRleCBpbiBhcC51cmFuZ2Uoc2VsZi5hZG1pbnMubGVuZ3RoKToKICAgIGZyYW1lX2RpZyAwCiAgICBmcmFtZV9kaWcgMQogICAgPAogICAgYnogdXBkYXRlX2FmdGVyX2ZvckA5CiAgICAvLyBzbWFydF9jb250cmFjdHMvemFpYmF0c3VfYmFzZS9jb250cmFjdC5weToyNgogICAgLy8gaWYgc2VsZi5hZG1pbnNbaW5kZXhdID09IGFwLlR4bi5zZW5kZXI6CiAgICBpbnQgMAogICAgYnl0ZSAiYWRtaW5zIgogICAgYXBwX2dsb2JhbF9nZXRfZXgKICAgIGFzc2VydCAvLyBjaGVjayBhZG1pbnMgZXhpc3RzCiAgICBkdXAKICAgIGludCAwCiAgICBleHRyYWN0X3VpbnQxNgogICAgZnJhbWVfZGlnIDAKICAgIGR1cAogICAgdW5jb3ZlciAyCiAgICA8CiAgICBhc3NlcnQgLy8gSW5kZXggYWNjZXNzIGlzIG91dCBvZiBib3VuZHMKICAgIHN3YXAKICAgIGV4dHJhY3QgMiAwCiAgICBzd2FwCiAgICBpbnQgMzIKICAgICoKICAgIGludCAzMgogICAgZXh0cmFjdDMKICAgIHR4biBTZW5kZXIKICAgID09CiAgICBieiB1cGRhdGVfYWZ0ZXJfaWZfZWxzZUA2CiAgICAvLyBzbWFydF9jb250cmFjdHMvemFpYmF0c3VfYmFzZS9jb250cmFjdC5weToyNwogICAgLy8gcmV0dXJuIFRydWUKICAgIGludCAxCiAgICBmcmFtZV9idXJ5IDAKICAgIHJldHN1YgoKdXBkYXRlX2FmdGVyX2lmX2Vsc2VANjoKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy96YWliYXRzdV9iYXNlL2NvbnRyYWN0LnB5OjI1CiAgICAvLyBmb3IgaW5kZXggaW4gYXAudXJhbmdlKHNlbGYuYWRtaW5zLmxlbmd0aCk6CiAgICBmcmFtZV9kaWcgMAogICAgaW50IDEKICAgICsKICAgIGZyYW1lX2J1cnkgMAogICAgYiB1cGRhdGVfZm9yX2hlYWRlckAzCgp1cGRhdGVfYWZ0ZXJfZm9yQDk6CiAgICAvLyBzbWFydF9jb250cmFjdHMvemFpYmF0c3VfYmFzZS9jb250cmFjdC5weToyOAogICAgLy8gcmV0dXJuIEZhbHNlCiAgICBpbnQgMAogICAgZnJhbWVfYnVyeSAwCiAgICByZXRzdWIKCgovLyBzbWFydF9jb250cmFjdHMuemFpYmF0c3VfYmFzZS5jb250cmFjdC5aYWliYXRzdUJhc2UuZGVsZXRlKCkgLT4gdWludDY0OgpkZWxldGU6CiAgICAvLyBzbWFydF9jb250cmFjdHMvemFpYmF0c3VfYmFzZS9jb250cmFjdC5weTozMC0zMQogICAgLy8gQGE0LmFiaW1ldGhvZChhbGxvd19hY3Rpb25zPVsiRGVsZXRlQXBwbGljYXRpb24iXSkKICAgIC8vIGRlZiBkZWxldGUoc2VsZikgLT4gYm9vbDoKICAgIHByb3RvIDAgMQogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6MzIKICAgIC8vIGlmIGFwLlR4bi5zZW5kZXIgPT0gb3AuR2xvYmFsLmNyZWF0b3JfYWRkcmVzczoKICAgIHR4biBTZW5kZXIKICAgIGdsb2JhbCBDcmVhdG9yQWRkcmVzcwogICAgPT0KICAgIGJ6IGRlbGV0ZV9hZnRlcl9pZl9lbHNlQDIKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy96YWliYXRzdV9iYXNlL2NvbnRyYWN0LnB5OjMzCiAgICAvLyByZXR1cm4gVHJ1ZQogICAgaW50IDEKICAgIHJldHN1YgoKZGVsZXRlX2FmdGVyX2lmX2Vsc2VAMjoKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy96YWliYXRzdV9iYXNlL2NvbnRyYWN0LnB5OjM0CiAgICAvLyByZXR1cm4gRmFsc2UKICAgIGludCAwCiAgICByZXRzdWIKCgovLyBzbWFydF9jb250cmFjdHMuemFpYmF0c3VfYmFzZS5jb250cmFjdC5aYWliYXRzdUJhc2Uub3B0X2NvbnRyYWN0X2ludG9fYXNzZXQoYXNzZXQ6IHVpbnQ2NCkgLT4gdWludDY0OgpvcHRfY29udHJhY3RfaW50b19hc3NldDoKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy96YWliYXRzdV9iYXNlL2NvbnRyYWN0LnB5OjM2LTM3CiAgICAvLyBAYTQuYWJpbWV0aG9kKCkKICAgIC8vIGRlZiBvcHRfY29udHJhY3RfaW50b19hc3NldChzZWxmLCBhc3NldDogYXAuQXNzZXQpIC0+IGJvb2w6CiAgICBwcm90byAxIDEKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy96YWliYXRzdV9iYXNlL2NvbnRyYWN0LnB5OjM4CiAgICAvLyBzZWxmLm9wdF9hcHBfaW50b19hc3NldChhc3NldCkKICAgIGZyYW1lX2RpZyAtMQogICAgY2FsbHN1YiBvcHRfYXBwX2ludG9fYXNzZXQKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy96YWliYXRzdV9iYXNlL2NvbnRyYWN0LnB5OjM5CiAgICAvLyByZXR1cm4gVHJ1ZQogICAgaW50IDEKICAgIHJldHN1YgoKCi8vIHNtYXJ0X2NvbnRyYWN0cy56YWliYXRzdV9iYXNlLmNvbnRyYWN0LlphaWJhdHN1QmFzZS5vcHRfYXBwX2ludG9fYXNzZXQoYXNzZXQ6IHVpbnQ2NCkgLT4gdm9pZDoKb3B0X2FwcF9pbnRvX2Fzc2V0OgogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6NDEtNDUKICAgIC8vICMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMKICAgIC8vICMjIyMjIyMjIyMjIyMjIyMjIyMjIyAgIFN1YnJvdXRpbmVzICAgICMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMKICAgIC8vICMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMKICAgIC8vIEBhcC5zdWJyb3V0aW5lCiAgICAvLyBkZWYgb3B0X2FwcF9pbnRvX2Fzc2V0KHNlbGYsIGFzc2V0OiBhcC5Bc3NldCkgLT4gTm9uZToKICAgIHByb3RvIDEgMAogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6NTAKICAgIC8vIGFzc2V0X3JlY2VpdmVyPWFwLkdsb2JhbC5jdXJyZW50X2FwcGxpY2F0aW9uX2FkZHJlc3MsCiAgICBnbG9iYWwgQ3VycmVudEFwcGxpY2F0aW9uQWRkcmVzcwogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6NTIKICAgIC8vIHR4bi5zdWJtaXQoKQogICAgaXR4bl9iZWdpbgogICAgaXR4bl9maWVsZCBBc3NldFJlY2VpdmVyCiAgICBmcmFtZV9kaWcgLTEKICAgIGl0eG5fZmllbGQgWGZlckFzc2V0CiAgICAvLyBzbWFydF9jb250cmFjdHMvemFpYmF0c3VfYmFzZS9jb250cmFjdC5weTo0NwogICAgLy8gYXNzZXRfYW1vdW50PTAsCiAgICBpbnQgMAogICAgaXR4bl9maWVsZCBBc3NldEFtb3VudAogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6NDYKICAgIC8vIHR4biA9IGFwLml0eG4uQXNzZXRUcmFuc2ZlcigKICAgIGludCBheGZlcgogICAgaXR4bl9maWVsZCBUeXBlRW51bQogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6NDgKICAgIC8vIGZlZT0xMDAwLAogICAgaW50IDEwMDAKICAgIGl0eG5fZmllbGQgRmVlCiAgICAvLyBzbWFydF9jb250cmFjdHMvemFpYmF0c3VfYmFzZS9jb250cmFjdC5weTo1MgogICAgLy8gdHhuLnN1Ym1pdCgpCiAgICBpdHhuX3N1Ym1pdAogICAgcmV0c3ViCgoKLy8gc21hcnRfY29udHJhY3RzLnphaWJhdHN1X2Jhc2UuY29udHJhY3QuWmFpYmF0c3VCYXNlLl9faW5pdF9fKCkgLT4gdm9pZDoKX19pbml0X186CiAgICAvLyBzbWFydF9jb250cmFjdHMvemFpYmF0c3VfYmFzZS9jb250cmFjdC5weToxMgogICAgLy8gZGVmIF9faW5pdF9fKHNlbGYpIC0+IE5vbmU6CiAgICBwcm90byAwIDAKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy96YWliYXRzdV9iYXNlL2NvbnRyYWN0LnB5OjEzCiAgICAvLyBzZWxmLmFkbWluczogQWRkcmVzc0FycmF5ID0gQWRkcmVzc0FycmF5KCkKICAgIGJ5dGUgImFkbWlucyIKICAgIGJ5dGUgMHgwMDAwCiAgICBhcHBfZ2xvYmFsX3B1dAogICAgLy8gc21hcnRfY29udHJhY3RzL3phaWJhdHN1X2Jhc2UvY29udHJhY3QucHk6MTQKICAgIC8vIHNlbGYuc2VydmljZV9jb250cmFjdDogYTQuQWRkcmVzcyA9IGE0LkFkZHJlc3MoKQogICAgYnl0ZSAic2VydmljZV9jb250cmFjdCIKICAgIGdsb2JhbCBaZXJvQWRkcmVzcwogICAgYXBwX2dsb2JhbF9wdXQKICAgIHJldHN1Ygo=",
        "clear": "I3ByYWdtYSB2ZXJzaW9uIDEwCgpzbWFydF9jb250cmFjdHMuemFpYmF0c3VfYmFzZS5jb250cmFjdC5aYWliYXRzdUJhc2UuY2xlYXJfc3RhdGVfcHJvZ3JhbToKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy96YWliYXRzdV9iYXNlL2NvbnRyYWN0LnB5OjExCiAgICAvLyBjbGFzcyBaYWliYXRzdUJhc2UoYXAuQVJDNENvbnRyYWN0KToKICAgIGludCAxCiAgICByZXR1cm4K"
    },
    "state": {
        "global": {
            "num_byte_slices": 2,
            "num_uints": 0
        },
        "local": {
            "num_byte_slices": 0,
            "num_uints": 0
        }
    },
    "schema": {
        "global": {
            "declared": {
                "admins": {
                    "type": "bytes",
                    "key": "admins"
                },
                "service_contract": {
                    "type": "bytes",
                    "key": "service_contract"
                }
            },
            "reserved": {}
        },
        "local": {
            "declared": {},
            "reserved": {}
        }
    },
    "contract": {
        "name": "ZaibatsuBase",
        "methods": [
            {
                "name": "create",
                "args": [],
                "returns": {
                    "type": "bool"
                }
            },
            {
                "name": "update",
                "args": [],
                "returns": {
                    "type": "bool"
                }
            },
            {
                "name": "delete",
                "args": [],
                "returns": {
                    "type": "bool"
                }
            },
            {
                "name": "opt_contract_into_asset",
                "args": [
                    {
                        "type": "asset",
                        "name": "asset"
                    }
                ],
                "returns": {
                    "type": "bool"
                }
            }
        ],
        "networks": {}
    },
    "bare_call_config": {}
}"""
APP_SPEC = algokit_utils.ApplicationSpecification.from_json(_APP_SPEC_JSON)
_TReturn = typing.TypeVar("_TReturn")


class _ArgsBase(ABC, typing.Generic[_TReturn]):
    @staticmethod
    @abstractmethod
    def method() -> str:
        ...


_TArgs = typing.TypeVar("_TArgs", bound=_ArgsBase[typing.Any])


@dataclasses.dataclass(kw_only=True)
class _TArgsHolder(typing.Generic[_TArgs]):
    args: _TArgs


@dataclasses.dataclass(kw_only=True)
class DeployCreate(algokit_utils.DeployCreateCallArgs, _TArgsHolder[_TArgs], typing.Generic[_TArgs]):
    pass


@dataclasses.dataclass(kw_only=True)
class Deploy(algokit_utils.DeployCallArgs, _TArgsHolder[_TArgs], typing.Generic[_TArgs]):
    pass


def _filter_none(value: dict | typing.Any) -> dict | typing.Any:
    if isinstance(value, dict):
        return {k: _filter_none(v) for k, v in value.items() if v is not None}
    return value


def _as_dict(data: typing.Any, *, convert_all: bool = True) -> dict[str, typing.Any]:
    if data is None:
        return {}
    if not dataclasses.is_dataclass(data):
        raise TypeError(f"{data} must be a dataclass")
    if convert_all:
        result = dataclasses.asdict(data)
    else:
        result = {f.name: getattr(data, f.name) for f in dataclasses.fields(data)}
    return _filter_none(result)


def _convert_transaction_parameters(
    transaction_parameters: algokit_utils.TransactionParameters | None,
) -> algokit_utils.TransactionParametersDict:
    return typing.cast(algokit_utils.TransactionParametersDict, _as_dict(transaction_parameters))


def _convert_call_transaction_parameters(
    transaction_parameters: algokit_utils.TransactionParameters | None,
) -> algokit_utils.OnCompleteCallParametersDict:
    return typing.cast(algokit_utils.OnCompleteCallParametersDict, _as_dict(transaction_parameters))


def _convert_create_transaction_parameters(
    transaction_parameters: algokit_utils.TransactionParameters | None,
    on_complete: algokit_utils.OnCompleteActionName,
) -> algokit_utils.CreateCallParametersDict:
    result = typing.cast(algokit_utils.CreateCallParametersDict, _as_dict(transaction_parameters))
    on_complete_enum = on_complete.replace("_", " ").title().replace(" ", "") + "OC"
    result["on_complete"] = getattr(algosdk.transaction.OnComplete, on_complete_enum)
    return result


def _convert_deploy_args(
    deploy_args: algokit_utils.DeployCallArgs | None,
) -> algokit_utils.ABICreateCallArgsDict | None:
    if deploy_args is None:
        return None

    deploy_args_dict = typing.cast(algokit_utils.ABICreateCallArgsDict, _as_dict(deploy_args))
    if isinstance(deploy_args, _TArgsHolder):
        deploy_args_dict["args"] = _as_dict(deploy_args.args)
        deploy_args_dict["method"] = deploy_args.args.method()

    return deploy_args_dict


@dataclasses.dataclass(kw_only=True)
class CreateArgs(_ArgsBase[bool]):
    @staticmethod
    def method() -> str:
        return "create()bool"


@dataclasses.dataclass(kw_only=True)
class OptContractIntoAssetArgs(_ArgsBase[bool]):
    asset: int

    @staticmethod
    def method() -> str:
        return "opt_contract_into_asset(asset)bool"


@dataclasses.dataclass(kw_only=True)
class UpdateArgs(_ArgsBase[bool]):
    @staticmethod
    def method() -> str:
        return "update()bool"


@dataclasses.dataclass(kw_only=True)
class DeleteArgs(_ArgsBase[bool]):
    @staticmethod
    def method() -> str:
        return "delete()bool"


class ByteReader:
    def __init__(self, data: bytes):
        self._data = data

    @property
    def as_bytes(self) -> bytes:
        return self._data

    @property
    def as_str(self) -> str:
        return self._data.decode("utf8")

    @property
    def as_base64(self) -> str:
        return base64.b64encode(self._data).decode("utf8")

    @property
    def as_hex(self) -> str:
        return self._data.hex()


class GlobalState:
    def __init__(self, data: dict[bytes, bytes | int]):
        self.admins = ByteReader(typing.cast(bytes, data.get(b"admins")))
        self.service_contract = ByteReader(typing.cast(bytes, data.get(b"service_contract")))


@dataclasses.dataclass(kw_only=True)
class SimulateOptions:
    allow_more_logs: bool = dataclasses.field(default=False)
    allow_empty_signatures: bool = dataclasses.field(default=False)
    extra_opcode_budget: int = dataclasses.field(default=0)
    exec_trace_config: models.SimulateTraceConfig | None         = dataclasses.field(default=None)


class Composer:

    def __init__(self, app_client: algokit_utils.ApplicationClient, atc: AtomicTransactionComposer):
        self.app_client = app_client
        self.atc = atc

    def build(self) -> AtomicTransactionComposer:
        return self.atc

    def simulate(self, options: SimulateOptions | None = None) -> SimulateAtomicTransactionResponse:
        request = models.SimulateRequest(
            allow_more_logs=options.allow_more_logs,
            allow_empty_signatures=options.allow_empty_signatures,
            extra_opcode_budget=options.extra_opcode_budget,
            exec_trace_config=options.exec_trace_config,
            txn_groups=[]
        ) if options else None
        result = self.atc.simulate(self.app_client.algod_client, request)
        return result

    def execute(self) -> AtomicTransactionResponse:
        return self.app_client.execute_atc(self.atc)

    def create(
        self,
        *,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> "Composer":
        """Adds a call to `create()bool` ABI method
        
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns Composer: This Composer instance"""

        args = CreateArgs()
        self.app_client.compose_call(
            self.atc,
            call_abi_method=args.method(),
            transaction_parameters=_convert_call_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return self

    def opt_contract_into_asset(
        self,
        *,
        asset: int,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> "Composer":
        """Adds a call to `opt_contract_into_asset(asset)bool` ABI method
        
        :param int asset: The `asset` ABI parameter
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns Composer: This Composer instance"""

        args = OptContractIntoAssetArgs(
            asset=asset,
        )
        self.app_client.compose_call(
            self.atc,
            call_abi_method=args.method(),
            transaction_parameters=_convert_call_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return self

    def create_create(
        self,
        *,
        on_complete: typing.Literal["no_op"] = "no_op",
        transaction_parameters: algokit_utils.CreateTransactionParameters | None = None,
    ) -> "Composer":
        """Adds a call to `create()bool` ABI method
        
        :param typing.Literal[no_op] on_complete: On completion type to use
        :param algokit_utils.CreateTransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns Composer: This Composer instance"""

        args = CreateArgs()
        self.app_client.compose_create(
            self.atc,
            call_abi_method=args.method(),
            transaction_parameters=_convert_create_transaction_parameters(transaction_parameters, on_complete),
            **_as_dict(args, convert_all=True),
        )
        return self

    def update_update(
        self,
        *,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> "Composer":
        """Adds a call to `update()bool` ABI method
        
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns Composer: This Composer instance"""

        args = UpdateArgs()
        self.app_client.compose_update(
            self.atc,
            call_abi_method=args.method(),
            transaction_parameters=_convert_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return self

    def delete_delete(
        self,
        *,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> "Composer":
        """Adds a call to `delete()bool` ABI method
        
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns Composer: This Composer instance"""

        args = DeleteArgs()
        self.app_client.compose_delete(
            self.atc,
            call_abi_method=args.method(),
            transaction_parameters=_convert_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return self

    def clear_state(
        self,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
        app_args: list[bytes] | None = None,
    ) -> "Composer":
        """Adds a call to the application with on completion set to ClearState
    
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :param list[bytes] | None app_args: (optional) Application args to pass"""
    
        self.app_client.compose_clear_state(self.atc, _convert_transaction_parameters(transaction_parameters), app_args)
        return self


class ZaibatsuBaseClient:
    """A class for interacting with the ZaibatsuBase app providing high productivity and
    strongly typed methods to deploy and call the app"""

    @typing.overload
    def __init__(
        self,
        algod_client: algosdk.v2client.algod.AlgodClient,
        *,
        app_id: int = 0,
        signer: TransactionSigner | algokit_utils.Account | None = None,
        sender: str | None = None,
        suggested_params: algosdk.transaction.SuggestedParams | None = None,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        app_name: str | None = None,
    ) -> None:
        ...

    @typing.overload
    def __init__(
        self,
        algod_client: algosdk.v2client.algod.AlgodClient,
        *,
        creator: str | algokit_utils.Account,
        indexer_client: algosdk.v2client.indexer.IndexerClient | None = None,
        existing_deployments: algokit_utils.AppLookup | None = None,
        signer: TransactionSigner | algokit_utils.Account | None = None,
        sender: str | None = None,
        suggested_params: algosdk.transaction.SuggestedParams | None = None,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        app_name: str | None = None,
    ) -> None:
        ...

    def __init__(
        self,
        algod_client: algosdk.v2client.algod.AlgodClient,
        *,
        creator: str | algokit_utils.Account | None = None,
        indexer_client: algosdk.v2client.indexer.IndexerClient | None = None,
        existing_deployments: algokit_utils.AppLookup | None = None,
        app_id: int = 0,
        signer: TransactionSigner | algokit_utils.Account | None = None,
        sender: str | None = None,
        suggested_params: algosdk.transaction.SuggestedParams | None = None,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        app_name: str | None = None,
    ) -> None:
        """
        ZaibatsuBaseClient can be created with an app_id to interact with an existing application, alternatively
        it can be created with a creator and indexer_client specified to find existing applications by name and creator.
        
        :param AlgodClient algod_client: AlgoSDK algod client
        :param int app_id: The app_id of an existing application, to instead find the application by creator and name
        use the creator and indexer_client parameters
        :param str | Account creator: The address or Account of the app creator to resolve the app_id
        :param IndexerClient indexer_client: AlgoSDK indexer client, only required if deploying or finding app_id by
        creator and app name
        :param AppLookup existing_deployments:
        :param TransactionSigner | Account signer: Account or signer to use to sign transactions, if not specified and
        creator was passed as an Account will use that.
        :param str sender: Address to use as the sender for all transactions, will use the address associated with the
        signer if not specified.
        :param TemplateValueMapping template_values: Values to use for TMPL_* template variables, dictionary keys should
        *NOT* include the TMPL_ prefix
        :param str | None app_name: Name of application to use when deploying, defaults to name defined on the
        Application Specification
            """

        self.app_spec = APP_SPEC
        
        # calling full __init__ signature, so ignoring mypy warning about overloads
        self.app_client = algokit_utils.ApplicationClient(  # type: ignore[call-overload, misc]
            algod_client=algod_client,
            app_spec=self.app_spec,
            app_id=app_id,
            creator=creator,
            indexer_client=indexer_client,
            existing_deployments=existing_deployments,
            signer=signer,
            sender=sender,
            suggested_params=suggested_params,
            template_values=template_values,
            app_name=app_name,
        )

    @property
    def algod_client(self) -> algosdk.v2client.algod.AlgodClient:
        return self.app_client.algod_client

    @property
    def app_id(self) -> int:
        return self.app_client.app_id

    @app_id.setter
    def app_id(self, value: int) -> None:
        self.app_client.app_id = value

    @property
    def app_address(self) -> str:
        return self.app_client.app_address

    @property
    def sender(self) -> str | None:
        return self.app_client.sender

    @sender.setter
    def sender(self, value: str) -> None:
        self.app_client.sender = value

    @property
    def signer(self) -> TransactionSigner | None:
        return self.app_client.signer

    @signer.setter
    def signer(self, value: TransactionSigner) -> None:
        self.app_client.signer = value

    @property
    def suggested_params(self) -> algosdk.transaction.SuggestedParams | None:
        return self.app_client.suggested_params

    @suggested_params.setter
    def suggested_params(self, value: algosdk.transaction.SuggestedParams | None) -> None:
        self.app_client.suggested_params = value

    def get_global_state(self) -> GlobalState:
        """Returns the application's global state wrapped in a strongly typed class with options to format the stored value"""

        state = typing.cast(dict[bytes, bytes | int], self.app_client.get_global_state(raw=True))
        return GlobalState(state)

    def create(
        self,
        *,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> algokit_utils.ABITransactionResponse[bool]:
        """Calls `create()bool` ABI method
        
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.ABITransactionResponse[bool]: The result of the transaction"""

        args = CreateArgs()
        result = self.app_client.call(
            call_abi_method=args.method(),
            transaction_parameters=_convert_call_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return result

    def opt_contract_into_asset(
        self,
        *,
        asset: int,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> algokit_utils.ABITransactionResponse[bool]:
        """Calls `opt_contract_into_asset(asset)bool` ABI method
        
        :param int asset: The `asset` ABI parameter
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.ABITransactionResponse[bool]: The result of the transaction"""

        args = OptContractIntoAssetArgs(
            asset=asset,
        )
        result = self.app_client.call(
            call_abi_method=args.method(),
            transaction_parameters=_convert_call_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return result

    def create_create(
        self,
        *,
        on_complete: typing.Literal["no_op"] = "no_op",
        transaction_parameters: algokit_utils.CreateTransactionParameters | None = None,
    ) -> algokit_utils.ABITransactionResponse[bool]:
        """Calls `create()bool` ABI method
        
        :param typing.Literal[no_op] on_complete: On completion type to use
        :param algokit_utils.CreateTransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.ABITransactionResponse[bool]: The result of the transaction"""

        args = CreateArgs()
        result = self.app_client.create(
            call_abi_method=args.method(),
            transaction_parameters=_convert_create_transaction_parameters(transaction_parameters, on_complete),
            **_as_dict(args, convert_all=True),
        )
        return result

    def update_update(
        self,
        *,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> algokit_utils.ABITransactionResponse[bool]:
        """Calls `update()bool` ABI method
        
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.ABITransactionResponse[bool]: The result of the transaction"""

        args = UpdateArgs()
        result = self.app_client.update(
            call_abi_method=args.method(),
            transaction_parameters=_convert_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return result

    def delete_delete(
        self,
        *,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> algokit_utils.ABITransactionResponse[bool]:
        """Calls `delete()bool` ABI method
        
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.ABITransactionResponse[bool]: The result of the transaction"""

        args = DeleteArgs()
        result = self.app_client.delete(
            call_abi_method=args.method(),
            transaction_parameters=_convert_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return result

    def clear_state(
        self,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
        app_args: list[bytes] | None = None,
    ) -> algokit_utils.TransactionResponse:
        """Calls the application with on completion set to ClearState
    
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :param list[bytes] | None app_args: (optional) Application args to pass
        :returns algokit_utils.TransactionResponse: The result of the transaction"""
    
        return self.app_client.clear_state(_convert_transaction_parameters(transaction_parameters), app_args)

    def deploy(
        self,
        version: str | None = None,
        *,
        signer: TransactionSigner | None = None,
        sender: str | None = None,
        allow_update: bool | None = None,
        allow_delete: bool | None = None,
        on_update: algokit_utils.OnUpdate = algokit_utils.OnUpdate.Fail,
        on_schema_break: algokit_utils.OnSchemaBreak = algokit_utils.OnSchemaBreak.Fail,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        create_args: DeployCreate[CreateArgs],
        update_args: Deploy[UpdateArgs],
        delete_args: Deploy[DeleteArgs],
    ) -> algokit_utils.DeployResponse:
        """Deploy an application and update client to reference it.
        
        Idempotently deploy (create, update/delete if changed) an app against the given name via the given creator
        account, including deploy-time template placeholder substitutions.
        To understand the architecture decisions behind this functionality please see
        <https://github.com/algorandfoundation/algokit-cli/blob/main/docs/architecture-decisions/2023-01-12_smart-contract-deployment.md>
        
        ```{note}
        If there is a breaking state schema change to an existing app (and `on_schema_break` is set to
        'ReplaceApp' the existing app will be deleted and re-created.
        ```
        
        ```{note}
        If there is an update (different TEAL code) to an existing app (and `on_update` is set to 'ReplaceApp')
        the existing app will be deleted and re-created.
        ```
        
        :param str version: version to use when creating or updating app, if None version will be auto incremented
        :param algosdk.atomic_transaction_composer.TransactionSigner signer: signer to use when deploying app
        , if None uses self.signer
        :param str sender: sender address to use when deploying app, if None uses self.sender
        :param bool allow_delete: Used to set the `TMPL_DELETABLE` template variable to conditionally control if an app
        can be deleted
        :param bool allow_update: Used to set the `TMPL_UPDATABLE` template variable to conditionally control if an app
        can be updated
        :param OnUpdate on_update: Determines what action to take if an application update is required
        :param OnSchemaBreak on_schema_break: Determines what action to take if an application schema requirements
        has increased beyond the current allocation
        :param dict[str, int|str|bytes] template_values: Values to use for `TMPL_*` template variables, dictionary keys
        should *NOT* include the TMPL_ prefix
        :param DeployCreate[CreateArgs] create_args: Arguments used when creating an application
        :param Deploy[UpdateArgs] update_args: Arguments used when updating an application
        :param Deploy[DeleteArgs] delete_args: Arguments used when deleting an application
        :return DeployResponse: details action taken and relevant transactions
        :raises DeploymentError: If the deployment failed"""

        return self.app_client.deploy(
            version,
            signer=signer,
            sender=sender,
            allow_update=allow_update,
            allow_delete=allow_delete,
            on_update=on_update,
            on_schema_break=on_schema_break,
            template_values=template_values,
            create_args=_convert_deploy_args(create_args),
            update_args=_convert_deploy_args(update_args),
            delete_args=_convert_deploy_args(delete_args),
        )

    def compose(self, atc: AtomicTransactionComposer | None = None) -> Composer:
        return Composer(self.app_client, atc or AtomicTransactionComposer())