import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { UserPlus, UserCog, FilePlus2, Users, Package } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';

export default function DashboardHome() {
  const navigate = useNavigate();

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">Welcome back, Admin. Here's what's happening today.</p>
      </div>

      <motion.div 
        variants={container}
        initial="hidden"
        animate="show"
        className="grid gap-4 md:grid-cols-3"
      >
        <motion.div variants={item} className="cursor-pointer" onClick={() => navigate('/dashboard/ledger')}>
            <Card className="hover:bg-accent/50 transition-colors border-primary/20 bg-primary/5">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Add to Ledger</CardTitle>
                    <UserPlus className="h-4 w-4 text-primary" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">Add Party</div>
                    <p className="text-xs text-muted-foreground">Register a new client</p>
                </CardContent>
            </Card>
        </motion.div>

        <motion.div variants={item} className="cursor-pointer" onClick={() => navigate('/dashboard/ledger')}>
            <Card className="hover:bg-accent/50 transition-colors">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Manage Parties</CardTitle>
                    <UserCog className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">Update Party</div>
                    <p className="text-xs text-muted-foreground">Edit details or checks status</p>
                </CardContent>
            </Card>
        </motion.div>

        <motion.div variants={item} className="cursor-pointer" onClick={() => navigate('/dashboard/transactions')}>
            <Card className="hover:bg-accent/50 transition-colors border-purple-500/20 bg-purple-500/5">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">New Rental</CardTitle>
                    <FilePlus2 className="h-4 w-4 text-purple-400" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">Create Transaction</div>
                    <p className="text-xs text-muted-foreground">Rent items & generate bill</p>
                </CardContent>
            </Card>
        </motion.div>
      </motion.div>

      {/* Quick Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
            <CardHeader>
                <CardTitle>Overview</CardTitle>
            </CardHeader>
            <CardContent className="pl-2">
                <div className="h-[200px] flex items-center justify-center text-muted-foreground">
                    Chart Placeholder
                </div>
            </CardContent>
        </Card>
        <Card className="col-span-3">
             <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>
                    You made 265 sales this month.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="flex items-center">
                            <div className="ml-4 space-y-1">
                                <p className="text-sm font-medium leading-none">John Doe</p>
                                <p className="text-sm text-muted-foreground">Rented 2 Printers</p>
                            </div>
                            <div className="ml-auto font-medium">+₹250.00</div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
      </div>
    </div>
  );
}
