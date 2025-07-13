from genie_client import GenieClient, GenieClientConfig
from genie_client.core import GenieClient  # Alternative import style

# Initialize client
config = GenieClientConfig(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tenant_id="your-tenant-id",
    databricks_url="https://your-workspace.cloud.databricks.com",
    workspace_id="1234567890",
    default_space_id="your-default-space"
)

client = GenieClient(config)

# Ask initial question
print("Asking initial question...")
response = client.ask_genie("Show top 5 customers by revenue")

if response.success:
    print(f"\n✅ Success! Operation took {response.duration_ms:.2f} ms")
    print(f"Status: {response.status}")
    print(f"Attachments: {len(response.attachments)}")
    
    if response.results:
        print(f"\nResults ({response.results['row_count']} rows):")
        for row in response.results["data"][:5]:
            print(row)
else:
    print(f"\n❌ Error: {response.error_message}")

# Ask follow-up question
if response.success and response.conversation_id:
    print("\nAsking follow-up question...")
    follow_up = client.ask_genie(
        question="Now show only active customers",
        space_id="your-space-id",
        follow_up=True,
        conversation_id=response.conversation_id
    )
    
    if follow_up.success:
        print("\n✅ Follow-up successful!")
        if follow_up.results:
            print(f"Retrieved {follow_up.results['row_count']} rows")
    else:
        print(f"\n❌ Follow-up failed: {follow_up.error_message}")