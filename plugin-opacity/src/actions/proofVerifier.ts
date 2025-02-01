import {
    ActionExample,
    IAgentRuntime, 
    Memory,
    State,
    HandlerCallback,
    type Action,
} from "@elizaos/core";
import { elizaLogger } from "@elizaos/core";

interface ProofVerificationResult {
    success: boolean;
    proofId: string;
    timestamp: number;
    verificationDetails?: {
        verifiedAt: number;
        verifier: string;
    };
}

interface ProofVerificationMemory extends Memory {
    content: {
        text: string;
        proofId: string;
        timestamp: number;
        actionType: string;
        verificationResult: boolean;
    };
    createdAt: number;
}

const validateVerificationRequest = async (runtime: IAgentRuntime, message: Memory): Promise<boolean> => {
    elizaLogger.info("🔍 Opacity: Validating proof verification request...");

    if (!runtime?.character?.settings?.secrets?.OPACITY_TEAM_ID || 
        !runtime?.character?.settings?.secrets?.OPACITY_PROVER_URL) {
        elizaLogger.error("❌ Opacity: API credentials not configured");
        return false;
    }

    // Check if proofId exists in the message
    const proofId = message.content?.proofId;
    if (!proofId) {
        elizaLogger.error("❌ Opacity: No proof ID provided for verification");
        return false;
    }

    elizaLogger.info("✅ Opacity: Verification request validation successful");
    return true;
};

const verifyProofWithOpacity = async (
    proverUrl: string,
    proofId: string
): Promise<ProofVerificationResult> => {
    try {
        const response = await fetch(`${proverUrl}/verify/${proofId}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            const errorMessage = `Opacity verification error (${response.status}): ${response.statusText}`;
            elizaLogger.error(`❌ ${errorMessage}`);
            throw new Error(errorMessage);
        }

        const result = await response.json() as { success: boolean };
        return {
            success: result.success,
            proofId: proofId,
            timestamp: Date.now(),
            verificationDetails: {
                verifiedAt: Date.now(),
                verifier: "opacity-prover"
            }
        };
    } catch (error) {
        elizaLogger.error('❌ Opacity proof verification failed:', error);
        throw new Error('Failed to verify proof. Please try again later.');
    }
};

const generateVerificationReport = (result: ProofVerificationResult): string => {
    return `🔐 Opacity Proof Verification Report
Powered by Opacity Prover

${result.success ? '✅ Proof Verified Successfully' : '❌ Proof Verification Failed'}
📝 Proof ID: ${result.proofId}
⏰ Verified At: ${new Date(result.verificationDetails?.verifiedAt || result.timestamp).toISOString()}
🔍 Verifier: ${result.verificationDetails?.verifier || 'Unknown'}

This verification confirms the authenticity of the proof
—————————————————`;
};

const extractProofFromTweet = (tweetText: string): string | null => {
    // Look for proof ID in the tweet text
    const proofIdMatch = tweetText.match(/Proof ID: ([a-zA-Z0-9-]+)/);
    return proofIdMatch ? proofIdMatch[1] : null;
};

export const verifyProof: Action = {
    name: "VERIFY_PROOF",
    similes: ["CHECK_PROOF", "VALIDATE_PROOF", "VERIFY_AUTONOMY", "CONFIRM_PROOF"],
    validate: validateVerificationRequest,
    description: "Verify a cryptographic proof of autonomous agent activity using Opacity",
    handler: async (
        runtime: IAgentRuntime,
        message: Memory,
        state: State,
        options: any,
        callback: HandlerCallback
    ): Promise<void> => {
        if (state['isProofVerificationInProgress']) return;
        state['isProofVerificationInProgress'] = true;

        elizaLogger.info("🔍 Opacity: Initiating proof verification...");
        
        const proverUrl = runtime.character?.settings?.secrets?.OPACITY_PROVER_URL;
        const proofId = message.content?.proofId || extractProofFromTweet(message.content?.text);

        if (!proofId) {
            throw new Error("No proof ID found in the message");
        }

        if (!proverUrl) {
            throw new Error("Missing proverURL");
        }

        try {
            const result = await verifyProofWithOpacity(proverUrl, proofId as string);

            elizaLogger.info(`${result.success ? '✅' : '❌'} Opacity: Proof verification complete`, {
                proofId: result.proofId,
                success: result.success,
                timestamp: result.timestamp
            });

            const verificationMemory: ProofVerificationMemory = {
                ...message,
                content: {
                    text: `Proof Verified: ${result.proofId}`,
                    proofId: result.proofId,
                    timestamp: result.timestamp,
                    actionType: "VERIFY_PROOF",
                    verificationResult: result.success
                },
                createdAt: Date.now()
            };

            await runtime.messageManager.createMemory(verificationMemory);
            
            callback({
                text: generateVerificationReport(result),
                proofId: result.proofId,
                success: result.success,
                timestamp: result.timestamp,
                verificationDetails: result.verificationDetails
            });

        } catch (error) {
            elizaLogger.error(`❌ Opacity: Proof verification error:`, error);
            throw new Error(`Proof verification failed: ${error.message}`);
        } finally {
            state['isProofVerificationInProgress'] = false;
        }
    },
    examples: [
        [
            {
                user: "{{user1}}",
                content: { 
                    text: "verify this proof",
                    proofId: "proof-123" 
                }
            },
            {
                user: "{{agentName}}",
                content: {
                    text: "I'll verify the cryptographic proof...",
                    action: "VERIFY_PROOF"
                }
            }
        ],
        [
            {
                user: "{{user1}}",
                content: { 
                    text: "check if this proof is valid",
                    proofId: "proof-456"
                }
            },
            {
                user: "{{agentName}}",
                content: {
                    text: "Let me validate this proof for you...",
                    action: "VERIFY_PROOF"
                }
            }
        ]
    ] as ActionExample[][],
} as Action;