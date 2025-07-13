from genie_client.config import PATGenieClientConfig
from genie_client.core.client import GenieClient


config = PATGenieClientConfig(
    personal_access_token="<PAT>",
    databricks_url="https://dbc-c6d167b8-12f9.cloud.databricks.com",
    workspace_id="12cd53492d274d98"
)

client = GenieClient(config)


# Ask initial question
print("Asking initial question...")
response = client.ask_genie(
    "What was our revenue in May 2024?",
    space_id="01f05f2aaafb1f948cc1ccf4d1055295",
)

print(response)
if response.success:
    print(f"\n✅ Success! Operation took {response.duration_ms:.2f} ms")
    print(f"Status: {response.status}")
    print(f"Attachments: {len(response.attachments)}")
    
    if response.results:
        print(f"\nResults ({response.results['row_count']} rows):")
        for row in response.results["data"][:5]:
            print(row)
    # Print response as a json object
    print("\nResponse:")
    print(response.model_dump_json())
else:
    print(f"\n❌ Error: {response.error_message}")

# Ask follow-up question
if response.success and response.conversation_id:
    print("\nAsking follow-up question...")
    follow_up = client.ask_genie(
        question="Give me all the details and list records contributed to revenue in the same above time period",
        space_id="01f05f2aaafb1f948cc1ccf4d1055295",
        follow_up=True,
        conversation_id=response.conversation_id
    )
    if follow_up.success:
        print("\n✅ Follow-up successful!")
        if follow_up.results:
            print(f"Retrieved {follow_up.results['row_count']} rows")
        with open("follow_up_response_1.json", "w") as f:
            f.write(follow_up.model_dump_json())
        f.close()
    else:
        print(f"\n❌ Follow-up failed: {follow_up.error_message}")

# Ask Second follow-up question
if response.success and response.conversation_id:
    print("\nAsking follow-up question...")
    follow_up = client.ask_genie(
        question="Provide me a description and a understanding on the data we have , that is being used so far in the conversation above.",
        space_id="01f05f2aaafb1f948cc1ccf4d1055295",
        follow_up=True,
        conversation_id=response.conversation_id
    )
    if follow_up.success:
        print("\n✅ Follow-up successful!")
        if follow_up.results:
            print(f"Retrieved {follow_up.results['row_count']} rows")
        with open("follow_up_response_2.json", "w") as f:
            f.write(follow_up.model_dump_json())
        f.close()
    else:
        print(f"\n❌ Follow-up failed: {follow_up.error_message}")