# src/game/agent_platform/integrations/phantom_wallet.py

from typing import Dict, Optional
import jwt
from solana.rpc.api import Client
from solana.transaction import Transaction
from datetime import datetime

class PhantomWalletIntegration:
    """    Integration with Phantom Wallet.
    """
        try:
            if not await self.verify_ownership(agent_id, wallet_address):

                transaction = await self._create_ownership_transaction(
                    agent_id,
                    wallet_address
                )

                result = await self._send_transaction(transaction)

                if result['success']:
                    self.connected_wallets[wallet_address]['agents'].append(agent_id)

                return result

            return {'success': False, 'reason': 'Agent already owned by wallet'}

        except Exception as e:
            return {'success': False, 'reason': str(e)}
