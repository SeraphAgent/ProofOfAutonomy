import {
    ActionExample,
    IAgentRuntime, 
    Memory,
    State,
    HandlerCallback,
    type Action,
} from "@elizaos/core";
import { elizaLogger } from "@elizaos/core";

interface ProofGenerationResult {
    success: boolean;
    proofId: string;
    timestamp: number;
}

interface ProofGenerationMemory extends Memory {
    content: {
        text: string;
        proofId: string;
        timestamp: number;
        actionType: string;
    };
    createdAt: number;
}

const validateProofRequest = async (runtime: IAgentRuntime, message: Memory): Promise<boolean> => {
    elizaLogger.info("🔍 Opacity: Validating proof generation request...");

    if (!runtime?.character?.settings?.secrets?.OPACITY_TEAM_ID || 
        !runtime?.character?.settings?.secrets?.OPACITY_PROVER_URL) {
        elizaLogger.error("❌ Opacity: API credentials not configured");
        return false;
    }

    elizaLogger.info("✅ Opacity: Request validation successful");
    return true;
};

const generateProofWithOpacity = async (teamId: string, proverUrl: string): Promise<ProofGenerationResult> => {
    try {
        const response = await fetch(`${proverUrl}/generate`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Team-ID": teamId
            },
            body: JSON.stringify({
                timestamp: Date.now()
            })
        });

        if (!response.ok) {
            const errorMessage = `Opacity API error (${response.status}): ${response.statusText}`;
            elizaLogger.error(`❌ ${errorMessage}`);
            throw new Error(errorMessage);
        }

        const result = await response.json();
        return {
            success: true,
            proofId: result.proofId,
            timestamp: result.timestamp
        };
    } catch (error) {
        elizaLogger.error('❌ Opacity proof generation failed:', error);
        throw new Error('Failed to generate proof. Please try again later.');
    }
};

const generateProofReport = (result: ProofGenerationResult): string => {
    return `🔐 Proof of Autonomy
📝 Proof ID: ${result.proofId}

@seraphagent Please verify this proof of autonomy activity.
—————————————————`;
};

export const generateProof: Action = {
    name: "GENERATE_PROOF",
    similes: ["PROVE_AUTONOMY", "VERIFY_AGENT", "CREATE_PROOF", "AUTONOMOUS_PROOF", "OPACITY_PROOF"],
    validate: validateProofRequest,
    description: "Generate a cryptographic proof of autonomous agent activity using Opacity",
    handler: async (
        runtime: IAgentRuntime,
        message: Memory,
        state: State,
        options: any,
        callback: HandlerCallback
    ): Promise<void> => {
        if (state['isProofGenerationInProgress']) return;
        state['isProofGenerationInProgress'] = true;

        elizaLogger.info("🤖 Opacity: Initiating proof generation...");
        
        const teamId = runtime.character?.settings?.secrets?.OPACITY_TEAM_ID;
        const proverUrl = runtime.character?.settings?.secrets?.OPACITY_PROVER_URL;

        if (!teamId || !proverUrl) {
            throw new Error("Opacity API credentials not configured");
        }

        try {
            const result = await generateProofWithOpacity(teamId, proverUrl);

            elizaLogger.info(`✅ Opacity: Proof generation complete`, {
                proofId: result.proofId,
                timestamp: result.timestamp
            });

            const proofMemory: ProofGenerationMemory = {
                ...message,
                content: {
                    text: `Proof Generated: ${result.proofId}`,
                    proofId: result.proofId,
                    timestamp: result.timestamp,
                    actionType: "GENERATE_PROOF"
                },
                createdAt: Date.now()
            };

            await runtime.messageManager.createMemory(proofMemory);
            
            callback({
                text: generateProofReport(result),
                proofId: result.proofId,
                timestamp: result.timestamp
            });

        } catch (error) {
            elizaLogger.error(`❌ Opacity: Proof generation error:`, error);
            throw new Error(`Proof generation failed: ${error.message}`);
        } finally {
            state['isProofGenerationInProgress'] = false;
        }
    },
    examples: [
        [
            {
                user: "{{user1}}",
                content: { text: "generate a proof of autonomy" }
            },
            {
                user: "{{agentName}}",
                content: {
                    text: "I'll generate a cryptographic proof of my autonomous activity...",
                    action: "GENERATE_PROOF"
                }
            }
        ],
        [
            {
                user: "{{user1}}",
                content: { text: "prove you're autonomous" }
            },
            {
                user: "{{agentName}}",
                content: {
                    text: "Let me create a proof to verify my autonomous nature...",
                    action: "GENERATE_PROOF"
                }
            }
        ]
    ] as ActionExample[][],
} as Action;
